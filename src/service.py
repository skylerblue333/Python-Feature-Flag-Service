from __future__ import annotations

from hashlib import sha256
from time import time
from typing import Final

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="Feature Flag Service", version="1.0.0")
flags_db: dict[str, "FeatureFlag"] = {}
FLAG_NAME_MAX_LENGTH: Final = 128


class FlagRule(BaseModel):
    enabled: bool
    percentage: int = Field(default=100, ge=0, le=100)
    user_ids: list[str] = Field(default_factory=list)


class FeatureFlag(BaseModel):
    name: str = Field(min_length=1, max_length=FLAG_NAME_MAX_LENGTH, pattern=r"^[a-zA-Z0-9_.-]+$")
    description: str = Field(min_length=1, max_length=500)
    rule: FlagRule
    updated_at: float = 0.0


@app.post("/flags", status_code=201)
def create_flag(flag: FeatureFlag) -> FeatureFlag:
    if flag.name in flags_db:
        raise HTTPException(status_code=409, detail="Flag already exists")
    stored = flag.model_copy(update={"updated_at": time()})
    flags_db[stored.name] = stored
    return stored


@app.get("/flags/{name}")
def get_flag(name: str) -> FeatureFlag:
    if name not in flags_db:
        raise HTTPException(status_code=404, detail="Flag not found")
    return flags_db[name]


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
    return {"enabled": bucket < rule.percentage, "reason": "percentage_rollout" if bucket < rule.percentage else "percentage_miss"}
