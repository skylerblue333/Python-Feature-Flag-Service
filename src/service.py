from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Optional
import time

app = FastAPI(title="Feature Flag Service")

class FlagRule(BaseModel):
    enabled: bool
    percentage: Optional[int] = 100
    user_ids: Optional[list[str]] = []

class FeatureFlag(BaseModel):
    name: str
    description: str
    rule: FlagRule
    updated_at: float = 0.0

flags_db: Dict[str, FeatureFlag] = {}

@app.post("/flags", status_code=201)
def create_flag(flag: FeatureFlag):
    flag.updated_at = time.time()
    flags_db[flag.name] = flag
    return flag

@app.get("/flags/{name}")
def get_flag(name: str):
    if name not in flags_db:
        raise HTTPException(status_code=404, detail="Flag not found")
    return flags_db[name]

@app.get("/evaluate/{name}/{user_id}")
def evaluate_flag(name: str, user_id: str):
    if name not in flags_db:
        return {"enabled": False, "reason": "not_found"}
    
    flag = flags_db[name]
    rule = flag.rule
    
    if not rule.enabled:
        return {"enabled": False, "reason": "globally_disabled"}
        
    if user_id in rule.user_ids:
        return {"enabled": True, "reason": "user_allowlist"}
        
    # Simple hash-based rollout
    user_hash = hash(user_id + name) % 100
    if user_hash < rule.percentage:
        return {"enabled": True, "reason": "percentage_rollout"}
        
    return {"enabled": False, "reason": "percentage_miss"}
