from fastapi import FastAPI
from pydantic import BaseModel
import planner_core 

app = FastAPI(title="Path Planner Evaluator")

class PlanningRequest(BaseModel):
    start: list[float]
    goal: list[float]
    heuristic_weight: float = 1.0

@app.post("/plan/ara-star")
def evaluate_ara_star(req: PlanningRequest):
    path = planner_core.plan_ara_star(req.start, req.goal, req.heuristic_weight)
    
    return {
        "algorithm": "ARA*", 
        "heuristic_weight": req.heuristic_weight,
        "path": path
    }
