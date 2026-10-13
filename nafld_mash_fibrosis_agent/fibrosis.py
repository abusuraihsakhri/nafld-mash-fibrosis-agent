"""Deterministic fibrosis indices for adult MASLD/NAFLD risk stratification.

FIB-4 and the historical NAFLD Fibrosis Score (NFS) estimate *risk* of
advanced fibrosis, not histological fibrosis stage, MASH, or drug eligibility.

References:
- AASLD Practice Guidance, Hepatology 2023;77:1797-1835.
  https://pmc.ncbi.nlm.nih.gov/articles/PMC10735173/
- Angulo et al., Hepatology 2007;45:846-854.
  https://doi.org/10.1002/hep.21496
"""
import math
from typing import Any, Dict, Optional


def _number(name: str, value: Any, low: float, high: float) -> float:
    if isinstance(value, bool):
        raise ValueError(f"{name} must be a number")
    try:
        number = float(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError(f"{name} must be a finite number") from exc
    if not math.isfinite(number) or not low <= number <= high:
        raise ValueError(f"{name} must be finite and between {low:g} and {high:g}")
    return number


def assess_fibrosis(
    age: float,
    ast: float,
    alt: float,
    platelets: float,
    *,
    bmi: Optional[float] = None,
    albumin: Optional[float] = None,
    impaired_fasting_glucose_or_diabetes: Optional[bool] = None,
) -> Dict[str, Any]:
    """Compute indices with laboratory units AST/ALT U/L, platelets 10^9/L.

    NFS requires *all* its additional inputs; absent values do not
    silently default to normal. This function accepts research inputs, not PHI.
    """
    age = _number("age (years)", age, 18, 120)
    ast = _number("AST (U/L)", ast, 0.01, 20000)
    alt = _number("ALT (U/L)", alt, 0.01, 20000)
    platelets = _number("platelets (10^9/L)", platelets, 0.01, 2000)
    if not age.is_integer():
        raise ValueError("age must be expressed in completed years")
    fib4 = age * ast / (platelets * math.sqrt(alt))
    lower = 2.0 if age > 65 else 1.3
    if fib4 > 2.67:
        category = "high"
        interpretation = "Above the high-risk threshold; specialist assessment is appropriate."
    elif fib4 < lower:
        category = "low"
        interpretation = "Below the age-adjusted low-risk threshold in appropriate settings."
    else:
        category = "indeterminate"
        interpretation = "Further fibrosis risk assessment (e.g. VCTE or ELF) may be warranted."

    cautions = [
        "Screening/risk stratification only: indices do not diagnose MASH, establish fibrosis stage, or determine pharmacotherapy eligibility.",
        "Do not interpret FIB-4 during acute illness or without clinical context.",
    ]
    if age < 35:
        cautions.append("FIB-4 is poorly accurate below age 35; consider secondary assessment when indicated.")
    if age > 65:
        cautions.append("Age >65: age-adjusted low-risk threshold of 2.0 applied.")
    result: Dict[str, Any] = {
        "fib4": round(fib4, 4),
        "fib4_category": category,
        "fib4_interpretation": interpretation,
        "fib4_low_risk_cutoff": lower,
        "fib4_high_risk_cutoff": 2.67,
        "nfs": None,
        "nfs_category": None,
        "cautions": cautions,
    }

    supplied = [bmi is not None, albumin is not None, impaired_fasting_glucose_or_diabetes is not None]
    if any(supplied) and not all(supplied):
        raise ValueError("NFS requires BMI, albumin and impaired fasting glucose/diabetes status together")
    if all(supplied):
        bmi = _number("BMI (kg/m^2)", bmi, 10, 100)
        albumin = _number("albumin (g/dL)", albumin, 0.1, 8)
        if not isinstance(impaired_fasting_glucose_or_diabetes, bool):
            raise ValueError("impaired_fasting_glucose_or_diabetes must be boolean")
        nfs = (
            -1.675 + 0.037 * age + 0.094 * bmi
            + 1.13 * int(impaired_fasting_glucose_or_diabetes)
            + 0.99 * (ast / alt) - 0.013 * platelets - 0.66 * albumin
        )
        result["nfs"] = round(nfs, 4)
        result["nfs_category"] = "low" if nfs < -1.455 else ("high" if nfs > 0.676 else "indeterminate")
        result["cautions"].append("NFS can overestimate advanced fibrosis in diabetes or obesity; interpret in clinical context.")
    return result
