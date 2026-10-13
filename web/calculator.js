/* Local-only deterministic FIB-4 and historical NAFLD Fibrosis Score. */
(function (root) {
  "use strict";

  function numberInRange(name, value, low, high) {
    if (value === "" || value === null || value === undefined || typeof value === "boolean") {
      throw new Error(name + " is required.");
    }
    const number = Number(value);
    if (!Number.isFinite(number) || number < low || number > high) {
      throw new Error(name + " must be between " + low + " and " + high + ".");
    }
    return number;
  }

  function calculateFibrosis(input) {
    if (!input || typeof input !== "object") throw new Error("Valid inputs are required.");
    const age = numberInRange("Age (years)", input.age, 18, 120);
    if (!Number.isInteger(age)) throw new Error("Age must be in completed years.");
    const ast = numberInRange("AST (U/L)", input.ast, 0.01, 20000);
    const alt = numberInRange("ALT (U/L)", input.alt, 0.01, 20000);
    const platelets = numberInRange("Platelets (10^9/L)", input.platelets, 0.01, 2000);
    const fib4 = age * ast / (platelets * Math.sqrt(alt));
    const lowCutoff = age > 65 ? 2.0 : 1.3;
    const fib4Category = fib4 > 2.67 ? "high" : fib4 < lowCutoff ? "low" : "indeterminate";
    const cautions = [
      "Indices estimate risk, not histological fibrosis stage, MASH or drug eligibility.",
      "FIB-4 should not be applied during acute illness."
    ];
    if (age < 35) cautions.push("FIB-4 is less accurate below age 35.");
    if (age > 65) cautions.push("The age-adjusted low-risk threshold of 2.0 is used.");

    const result = {
      fib4: Math.round(fib4 * 10000) / 10000,
      fib4_category: fib4Category,
      fib4_low_risk_cutoff: lowCutoff,
      fib4_high_risk_cutoff: 2.67,
      nfs: null,
      nfs_category: null,
      cautions: cautions
    };
    const provided = [input.bmi, input.albumin, input.impaired_fasting_glucose_or_diabetes]
      .map((x) => x !== "" && x !== null && x !== undefined);
    if (provided.some(Boolean) && !provided.every(Boolean)) {
      throw new Error("For NFS, provide BMI, albumin and glucose/diabetes status together.");
    }
    if (provided.every(Boolean)) {
      const bmi = numberInRange("BMI (kg/m²)", input.bmi, 10, 100);
      const albumin = numberInRange("Albumin (g/dL)", input.albumin, 0.1, 8);
      if (typeof input.impaired_fasting_glucose_or_diabetes !== "boolean") {
        throw new Error("Glucose/diabetes status must be Yes or No.");
      }
      const nfs = -1.675 + 0.037 * age + 0.094 * bmi +
        1.13 * Number(input.impaired_fasting_glucose_or_diabetes) +
        0.99 * (ast / alt) - 0.013 * platelets - 0.66 * albumin;
      result.nfs = Math.round(nfs * 10000) / 10000;
      result.nfs_category = nfs < -1.455 ? "low" : nfs > 0.676 ? "high" : "indeterminate";
      cautions.push("NFS can overestimate risk in people with obesity or diabetes.");
    }
    return result;
  }

  root.calculateFibrosis = calculateFibrosis;
  if (typeof module !== "undefined" && module.exports) module.exports = { calculateFibrosis };
})(typeof window !== "undefined" ? window : globalThis);
