# False Positive Conflicts

Total pairs: **2**

## 33_48

- Gold class: `not labeled`
- Predicted verdict: `incompatible`
- Confidence: `0.94`
- R33: Each field name in the Paths Object MUST begin with a backslash (\).
- R48: Each Specification Extension field name MUST begin with x-.
- Final reasoning: The strongest grounded reading establishes overlap: a Specification Extension field can appear inside a Paths Object. On that shared target, A requires the field name to begin with "\\", while B requires it to begin with "x-". A single field name cannot simultaneously begin with both prefixes, so the pair is textually inconsistent and impossible to jointly satisfy for that overlapping case. Compatibility survives only by assuming the categories never overlap, but that split was explicitly challenged and rebutted with spec-grounded support.

## 43_48

- Gold class: `not labeled`
- Predicted verdict: `incompatible`
- Confidence: `0.94`
- R43: Each field name in the Paths Object MUST begin with a backslash (\).
- R48: Each Specification Extension field name MUST begin with x-.
- Final reasoning: The strongest grounded reading establishes overlap: a Specification Extension field can appear inside a Paths Object. On that shared target, A requires the field name to begin with "\\", while B requires it to begin with "x-". A single field name cannot simultaneously begin with both prefixes, so the pair is textually inconsistent and impossible to jointly satisfy for that overlapping case. Compatibility survives only by assuming the categories never overlap, but that split was explicitly challenged and rebutted with spec-grounded support.
