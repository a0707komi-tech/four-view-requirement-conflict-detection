# False Positive Conflicts

Total pairs: **1**

## 51_53

- Gold class: `not labeled`
- Predicted verdict: `incompatible`
- Confidence: `0.91`
- R51: Only the seller agent shall be able to marked an under contract MLS listing as sold.
- R53: The agent shall be able to lookup and update any property listings in the MLS
- Final reasoning: Requirement A makes marking an under-contract MLS listing as sold exclusive to the seller agent. Requirement B says the agent can update any property listing in the MLS, and marking a listing as sold is a type of update. So B grants a broader permission that conflicts with A's exclusivity constraint.
