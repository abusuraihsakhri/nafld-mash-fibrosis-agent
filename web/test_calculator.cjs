"use strict";
const assert = require("node:assert/strict");
const { calculateFibrosis } = require("./calculator.js");

const base = { age: 60, ast: 30, alt: 40, platelets: 250 };
const result = calculateFibrosis(base);
assert.equal(result.fib4_category, "low");
assert.ok(Math.abs(result.fib4 - 60 * 30 / (250 * Math.sqrt(40))) < 0.00005);
assert.equal(result.nfs, null);

const older = calculateFibrosis({ age: 70, ast: 40, alt: 40, platelets: 240 });
assert.equal(older.fib4_low_risk_cutoff, 2);
assert.equal(older.fib4_category, "low");

const high = calculateFibrosis({ age: 55, ast: 90, alt: 35, platelets: 120 });
assert.equal(high.fib4_category, "high");

const nfs = calculateFibrosis({
  age: 52, ast: 40, alt: 50, platelets: 230,
  bmi: 29, albumin: 4.2, impaired_fasting_glucose_or_diabetes: true
});
const expected = -1.675 + 0.037 * 52 + 0.094 * 29 + 1.13 +
  0.99 * (40 / 50) - 0.013 * 230 - 0.66 * 4.2;
assert.ok(Math.abs(nfs.nfs - expected) < 0.00005);

for (const input of [
  { ...base, ast: NaN }, { ...base, alt: 0 },
  { ...base, platelets: 0 }, { ...base, age: 130 },
  { ...base, bmi: 30 }, { ...base, bmi: 30, albumin: 4 },
  { ...base, bmi: 30, albumin: 4, impaired_fasting_glucose_or_diabetes: "false" }
]) {
  assert.throws(() => calculateFibrosis(input), Error);
}
console.log("Browser calculator tests passed");
