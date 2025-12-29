from fastapi import APIRouter

router = APIRouter()

@router.get("/status")
def get_waf_status():
    return {"status": "active", "blocked_requests": 120, "bypasses_detected": 5}

@router.post("/rules")
def add_waf_rule(rule: dict):
    return {"message": "Rule added", "rule": rule}
