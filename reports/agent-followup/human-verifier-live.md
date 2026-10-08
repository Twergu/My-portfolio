# Human-reviewed Verifier calibration

Real Verifier API on eight human-reviewed candidate/evidence pairs. Offline calibration, not end-to-end Agent quality; constructed candidates include four intentional errors. Reviewer saw proposed references; not blind or independent adjudication. New threshold rule used these cases for development, so this is not a held-out test.

```json
{
  "completed": 8,
  "expected": 8,
  "complete": true,
  "errors": 0,
  "agreement": 0.875,
  "tp": 3,
  "fp": 0,
  "fn": 1,
  "tn": 4,
  "precision": 1.0,
  "recall": 0.75
}
```
