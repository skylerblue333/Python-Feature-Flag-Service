from __future__ import annotations

from hashlib import sha256
from time import time
from typing import Final

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="Sky Feature Flags", version="1.0.0")
flags_db: dict[str, "FeatureFlag"] = {}
FLAG_NAME_MAX_LENGTH: Final = 128
MAX_ALLOWLIST_USERS: Final = 1000


class FlagRule(BaseModel):
    enabled: bool
    percentage: int = Field(default=100, ge=0, le=100)
    user_ids: list[str] = Field(default_factory=list, max_length=MAX_ALLOWLIST_USERS)


class FeatureFlag(BaseModel):
    name: str = Field(min_length=1, max_length=FLAG_NAME_MAX_LENGTH, pattern=r"^[a-zA-Z0-9_.-]+$")
    description: str = Field(min_length=1, max_length=500)
    rule: FlagRule
    updated_at: float = 0.0


class FlagUpdate(BaseModel):
    description: str | None = Field(default=None, min_length=1, max_length=500)
    rule: FlagRule | None = None


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/ready")
def ready() -> dict[str, bool]:
    return {"ready": True}


@app.post("/flags", status_code=201)
def create_flag(flag: FeatureFlag) -> FeatureFlag:
    if flag.name in flags_db:
        raise HTTPException(status_code=409, detail="Flag already exists")
    stored = flag.model_copy(update={"updated_at": time()})
    flags_db[stored.name] = stored
    return stored


@app.get("/flags")
def list_flags() -> list[FeatureFlag]:
    return [flags_db[name] for name in sorted(flags_db)]


@app.get("/flags/{name}")
def get_flag(name: str) -> FeatureFlag:
    flag = flags_db.get(name)
    if flag is None:
        raise HTTPException(status_code=404, detail="Flag not found")
    return flag


@app.patch("/flags/{name}")
def update_flag(name: str, update: FlagUpdate) -> FeatureFlag:
    current = flags_db.get(name)
    if current is None:
        raise HTTPException(status_code=404, detail="Flag not found")
    changes = update.model_dump(exclude_none=True)
    if "rule" in changes:
        changes["rule"] = FlagRule.model_validate(changes["rule"])
    stored = current.model_copy(update={**changes, "updated_at": time()})
    flags_db[name] = stored
    return stored


@app.delete("/flags/{name}", status_code=204)
def delete_flag(name: str) -> None:
    if flags_db.pop(name, None) is None:
        raise HTTPException(status_code=404, detail="Flag not found")


@app.get("/evaluate/{name}/{user_id}")
def evaluate_flag(name: str, user_id: str) -> dict[str, bool | str]:
    flag = flags_db.get(name)
    if flag is None:
        return {"enabled": False, "reason": "not_found"}
    rule = flag.rule
    if not rule.enabled:
        return {"enabled": False, "reason": "globally_disabled"}
    if user_id in rule.user_ids:
        return {"enabled": True, "reason": "user_allowlist"}
    bucket = int.from_bytes(sha256(f"{name}:{user_id}".encode()).digest()[:4], "big") % 100
    enabled = bucket < rule.percentage
    return {
        "enabled": enabled,
        "reason": "percentage_rollout" if enabled else "percentage_miss",
    }
