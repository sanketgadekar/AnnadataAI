from typing import Dict
from .rules import compute_grade

def assess_soil(input_dict: Dict) -> Dict:
    """
    Input: raw dict (N,P,K,pH,OC,...)
    Output: standard JSON dict with grade, problems, improvement_plan, explainability
    """
    grade, problems, plan, explain = compute_grade(input_dict)
    return {
        "grade": grade,
        "problems": problems,
        "improvement_plan": plan,
        "explainability": explain
    }
