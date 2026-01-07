import json
from pathlib import Path
from typing import Dict, List, Tuple, Any

# Load thresholds.json (will raise FileNotFoundError if missing)
TH_PATH = Path(__file__).parent / "config" / "thresholds.json"
TH = json.load(open(TH_PATH))
T = TH["default"]
GRADE_RULES = TH.get("grade_rules", {}).get("poor_condition", {})


def safe_float(v):
    try:
        return None if v is None else float(v)
    except Exception:
        return None


def categorize_param(name: str, value: float) -> str:
    """Return category for a parameter: Low / Medium / High for nutrients; Acidic/Neutral/Alkaline for pH."""
    if value is None:
        return "Unknown"

    if name in ("N", "P", "K"):
        th = T[name]
        if value < th["medium"]:
            return "Low"
        if value < th["high"]:
            return "Medium"
        return "High"

    if name == "OC":
        th = T["OC"]
        if value < th["medium"]:
            return "Low"
        if value < th["high"]:
            return "Medium"
        return "High"

    if name == "pH":
        if value < T["pH"]["acidic"]:
            return "Acidic"
        if value > T["pH"]["alkaline"]:
            return "Alkaline"
        return "Neutral"

    return "Unknown"


def rule_text(param: str, category: str) -> str:
    """Return a human-readable rule text used in explainability."""
    if param in ("N", "P", "K"):
        th = T[param]
        if category == "Low":
            return f"< {th['medium']} => Low"
        if category == "Medium":
            return f"{th['medium']} <= value < {th['high']} => Medium"
        return f">= {th['high']} => High"
    if param == "OC":
        th = T["OC"]
        if category == "Low":
            return f"< {th['medium']} => Low"
        if category == "Medium":
            return f"{th['medium']} <= value < {th['high']} => Medium"
        return f">= {th['high']} => High"
    if param == "pH":
        if category == "Acidic":
            return f"< {T['pH']['acidic']} => Acidic"
        if category == "Alkaline":
            return f"> {T['pH']['alkaline']} => Alkaline"
        return f"{T['pH']['acidic']} <= value <= {T['pH']['alkaline']} => Neutral"
    return ""


def generate_combination_plan(problems: List[str], categories: Dict[str, Dict[str, Any]], inputs: Dict[str, Any]) -> List[str]:
    """
    Build prioritized, combination-aware improvement plan.
    Use conservative, general recommendations; swap with local extension tables when available.
    """
    plan: List[str] = []

    # Combined P + OC deficiency: prioritize both P application and organic matter
    if "Low P" in problems and "Low OC" in problems:
        plan.append("Apply 20 kg P/ha as single super phosphate (SSP) at sowing to correct phosphorus.")
        plan.append("Add 2 t/ha farmyard manure or compost before planting to raise organic carbon and improve P availability.")
    else:
        if "Low P" in problems:
            pH_cat = categories.get("pH", {}).get("category")
            if pH_cat == "Acidic":
                plan.append("Apply 20 kg P/ha as SSP at sowing and consider band application; acidic soils reduce P availability.")
            elif pH_cat == "Alkaline":
                plan.append("Apply 20 kg P/ha as SSP or DAP with banding; consider long-term acidifying practices if needed.")
            else:
                plan.append("Apply 20 kg P/ha as single super phosphate at sowing (banding recommended).")

    # N deficiency
    if "Low N" in problems:
        plan.append("Apply nitrogen in split doses (e.g., 50% at sowing, 50% at vegetative stage) using recommended N sources (urea/other).")

    # K deficiency
    if "Low K" in problems:
        plan.append("Apply potassium (e.g., muriate of potash) according to crop needs; split application recommended for some crops.")

    # OC only deficiency
    if "Low OC" in problems and "Low P" not in problems:
        plan.append("Apply 2–5 t/ha farmyard manure or compost annually and use cover crops/green manures to build organic carbon.")

    # pH issues
    if any(p == "Acidic pH" for p in problems) or categories.get("pH", {}).get("category") == "Acidic":
        plan.append("Soil is acidic — apply lime based on a buffer pH test; small initial liming improves P availability.")
    if any(p == "Alkaline pH" for p in problems) or categories.get("pH", {}).get("category") == "Alkaline":
        plan.append("Soil is alkaline — consider gypsum and organic matter to improve structure and nutrient availability.")

    # If still empty, healthy message
    if not plan:
        plan.append("Soil appears adequate — maintain balanced fertilization and organic matter management.")

    # dedupe while preserving order
    seen = set()
    deduped = []
    for p in plan:
        if p not in seen:
            deduped.append(p)
            seen.add(p)
    return deduped


def compute_grade(inputs: Dict[str, Any]) -> Tuple[str, List[str], List[str], Dict[str, Dict[str, Any]]]:
    """
    Main function.
    Inputs: dict possibly containing keys N,P,K,pH,OC (numeric) and optional crop, soil_type
    Returns: (grade, problems, improvement_plan, explainability)
    """
    # normalize values
    values = {}
    for k in ("N", "P", "K", "pH", "OC"):
        values[k] = safe_float(inputs.get(k))

    # categorize each parameter and build explainability
    categories: Dict[str, Dict[str, Any]] = {}
    problems: List[str] = []
    low_count = 0

    for param in ("N", "P", "K", "OC", "pH"):
        val = values.get(param)
        cat = categorize_param(param, val)
        categories[param] = {"value": val, "category": cat, "rule": rule_text(param, cat)}

        if param in ("N", "P", "K") and cat == "Low":
            problems.append(f"Low {param}")
            low_count += 1
        if param == "OC" and cat == "Low":
            problems.append("Low OC")
            low_count += 1
        if param == "pH" and cat in ("Acidic", "Alkaline"):
            problems.append(f"{cat} pH")

    # final grading logic (fixed & conservative)
    # - Good: no Low nutrients and pH neutral
    # - Fair: exactly one Low OR any Medium present but no Low? (we set Fair for 1 Low)
    # - Poor: 2 or more Low OR OC low flagged
    if low_count == 0 and not any(p.endswith("pH") for p in problems):
        grade = "Good"
    elif low_count == 1:
        grade = "Fair"
    else:
        grade = "Poor"

    # combination-aware improvement plan
    plan = generate_combination_plan(problems, categories, inputs)

    # build explainability dictionary (clean)
    explainability: Dict[str, Dict[str, Any]] = {}
    for param, meta in categories.items():
        explainability[param] = {
            "value": meta["value"],
            "category": meta["category"],
            "rule": meta["rule"]
        }

    return grade, problems, plan, explainability


# Simple runner for debugging
if __name__ == "__main__":
    sample = {"N": 120, "P": 8, "K": 85, "pH": 5.8, "OC": 0.45}
    grade, problems, plan, explain = compute_grade(sample)
    print("grade:", grade)
    print("problems:", problems)
    print("plan:", plan)
    print("explainability:", explain)
