# Missed Conflicts

Total pairs: **13**

## 3_10

- Gold class: `conflict`
- Predicted verdict: `uncertain`
- Confidence: `0.86`
- R3: Basic track to train and train to track information via continuous transmission media, i.e. radio. The train detection is provided by trackside
- R10: ETCS shall not be required to provide any track-to-train or train-to-track information via continuous transmissionmedia, i.e. radio.
- Final reasoning: The pair is textually anchored to the same capability: track-to-train and train-to-track information via continuous radio. If both applied to ETCS, they would be inconsistent, because A affirms that radio-based exchange is a basic function while B says ETCS shall not be required to provide that function. But the decisive scope premise is missing: A never names ETCS, while B does. A may describe a broader or different system, so the conflict cannot be conclusively grounded from the pair text alone.

## 13_58

- Gold class: `conflict`
- Predicted verdict: `compatible`
- Confidence: `0.9`
- R13: ETCS shall not be compatible with any national systems listed in the CCS TSI.
- R58: ETCS shall only be compatible with national systems listed in the CCS TSI if those systems are also equipped withETCS.
- Final reasoning: Both requirements are anchored to the same compatibility relation: ETCS versus national systems listed in the CCS TSI. But the strongest text-faithful reading does not establish conflict. A is an absolute prohibition: ETCS must not be compatible with any listed national system. B is a necessary-condition restriction: if ETCS is compatible with a listed national system, that system must also be ETCS-equipped. B does not explicitly require any such compatibility to exist. Therefore A can be satisfied, and B remains true vacuously. The incompatible analyses depend on reading B as a positive obligation to allow compatibility under the condition, which is not supported by the wording.

## 17_38

- Gold class: `conflict`
- Predicted verdict: `compatible`
- Confidence: `0.925`
- R17: track to train information provided by national system. Onboard functions provided by national system (STM) inco-operation with onboard ETCS.
- R38: ETCS is required to be functional to a maximum train speed of 500 km/h.
- Final reasoning: Skipped debate and arbitration because all four phase-1 agents produced the same verdict.

## 17_49

- Gold class: `conflict`
- Predicted verdict: `compatible`
- Confidence: `0.925`
- R17: track to train information provided by national system. Onboard functions provided by national system (STM) inco-operation with onboard ETCS.
- R49: ETCS is required to be functional to a maximum train speed of 500 km/h.
- Final reasoning: Skipped debate and arbitration because all four phase-1 agents produced the same verdict.

## 18_61

- Gold class: `conflict`
- Predicted verdict: `uncertain`
- Confidence: `0.78`
- R18: ETCS is required to be functional to a maximum train speed of 600 km/h.
- R61: ETCS shall only provide the driver with information to allow him to drive the train safely if the train speed is below400 km/h.
- Final reasoning: Both requirements are anchored to the same target (ETCS) and the same constraint dimension/condition (train speed). However, the decisive question is unresolved by the text alone: whether A’s requirement that ETCS be “functional” up to 600 km/h necessarily includes the specific driver-information function constrained by B. If it does, the pair is incompatible over 400–600 km/h; if not, they can coexist. The surviving compatible path and incompatible path both depend on that unstated scope assumption, so no conflict relation is textually established with enough certainty.

## 22_38

- Gold class: `conflict`
- Predicted verdict: `compatible`
- Confidence: `0.925`
- R22: track to train information provided by national system. Onboard functions provided by national system (STM) inco-operation with onboard ETCS.
- R38: ETCS is required to be functional to a maximum train speed of 500 km/h.
- Final reasoning: Skipped debate and arbitration because all four phase-1 agents produced the same verdict.

## 22_49

- Gold class: `conflict`
- Predicted verdict: `compatible`
- Confidence: `0.925`
- R22: track to train information provided by national system. Onboard functions provided by national system (STM) inco-operation with onboard ETCS.
- R49: ETCS is required to be functional to a maximum train speed of 500 km/h.
- Final reasoning: Skipped debate and arbitration because all four phase-1 agents produced the same verdict.

## 36_63

- Gold class: `conflict`
- Predicted verdict: `compatible`
- Confidence: `0.79`
- R36: Once received onboard the national values shall remain valid even if the onboard equipment is switched off.
- R63: national values received from the trackside shall be valid only for a limited time, after which they will beautomatically deleted from the onboard equipment.
- Final reasoning: Both requirements are anchored to the same item: onboard national values and their validity persistence. But A only says the values remain valid despite the equipment being switched off; it does not explicitly require unlimited validity. B says those same values are valid only for a limited time and are then automatically deleted. These can coexist textually: the values may stay valid through power-off periods, yet still expire after the specified time limit. The main incompatible readings depend on adding an unstated assumption that A means indefinite validity, which the text does not say.

## 37_61

- Gold class: `conflict`
- Predicted verdict: `compatible`
- Confidence: `0.93`
- R37: ETCS shall only be functional up to a maximum train speed of 100 km/h.
- R61: ETCS shall only provide the driver with information to allow him to drive the train safely if the train speed is below400 km/h.
- Final reasoning: Both requirements are anchored to ETCS and train speed, but the strongest text-faithful reading does not establish conflict. A says ETCS is functional only up to 100 km/h, i.e. above 100 km/h it must not be functional. B does not require ETCS to provide information throughout the whole range below 400 km/h; it only restricts provision so that, if ETCS provides such information, train speed must be below 400 km/h. Thus one implementation can satisfy both by being functional only at or below 100 km/h and providing information only within that functional range. No interference, inconsistency, or impossible joint satisfaction is textually forced.

## 38_61

- Gold class: `conflict`
- Predicted verdict: `uncertain`
- Confidence: `0.78`
- R38: ETCS is required to be functional to a maximum train speed of 500 km/h.
- R61: ETCS shall only provide the driver with information to allow him to drive the train safely if the train speed is below400 km/h.
- Final reasoning: Both requirements are anchored to the same system (ETCS) and speed condition, but their capability overlap is only partial. A requires ETCS to be functional up to 500 km/h. B restricts one specific function: providing the driver with information for safe driving only below 400 km/h. A conflict is established only if 'functional' in A is textually understood to include that specific driver-information function across the full 0–500 km/h range. The pair does not explicitly say that. Conversely, calling them fully compatible also depends on assuming A allows ETCS to remain functional above 400 km/h without that information service. That decisive assumption is unresolved from the text alone.

## 41_63

- Gold class: `conflict`
- Predicted verdict: `compatible`
- Confidence: `0.79`
- R41: Once received onboard the national values shall remain valid even if the onboard equipment is switched off.
- R63: national values received from the trackside shall be valid only for a limited time, after which they will beautomatically deleted from the onboard equipment.
- Final reasoning: Both requirements are anchored to the same item: onboard national values and their validity persistence. But A only says the values remain valid despite the equipment being switched off; it does not explicitly require unlimited validity. B says those same values are valid only for a limited time and are then automatically deleted. These can coexist textually: the values may stay valid through power-off periods, yet still expire after the specified time limit. The main incompatible readings depend on adding an unstated assumption that A means indefinite validity, which the text does not say.

## 46_63

- Gold class: `conflict`
- Predicted verdict: `compatible`
- Confidence: `0.9375`
- R46: If an ETCS equipped train passes a level transition to a line fitted with more than one level, the onboard shallswitch to the highest level, according to the priority given by trackside, for which it is equipped
- R63: national values received from the trackside shall be valid only for a limited time, after which they will beautomatically deleted from the onboard equipment.
- Final reasoning: Skipped debate and arbitration because all four phase-1 agents produced the same verdict.

## 49_61

- Gold class: `conflict`
- Predicted verdict: `uncertain`
- Confidence: `0.78`
- R49: ETCS is required to be functional to a maximum train speed of 500 km/h.
- R61: ETCS shall only provide the driver with information to allow him to drive the train safely if the train speed is below400 km/h.
- Final reasoning: Both requirements are anchored to the same system (ETCS) and speed condition, but their capability overlap is only partial. A requires ETCS to be functional up to 500 km/h. B restricts one specific function: providing the driver with information for safe driving only below 400 km/h. A conflict is established only if 'functional' in A is textually understood to include that specific driver-information function across the full 0–500 km/h range. The pair does not explicitly say that. Conversely, calling them fully compatible also depends on assuming A allows ETCS to remain functional above 400 km/h without that information service. That decisive assumption is unresolved from the text alone.
