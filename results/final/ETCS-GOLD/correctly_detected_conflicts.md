# Correctly Detected Conflicts

Total pairs: **36**

## 1_42

- Gold class: `conflict`
- Predicted verdict: `incompatible`
- Confidence: `0.925`
- R1: The current operational status shall be indicated to the driver on the DMI
- R42: ETCS shall not provide any information to the driver during level transitions.
- Final reasoning: Skipped debate and arbitration because all four phase-1 agents produced the same verdict.

## 2_42

- Gold class: `conflict`
- Predicted verdict: `incompatible`
- Confidence: `0.91`
- R2: The current application level shall be indicated on the DMI.
- R42: ETCS shall not provide any information to the driver during level transitions.
- Final reasoning: The pair overlaps on the same information channel and operating condition: ETCS/DMI information shown to the driver during level transitions. A requires the current application level to be indicated on the DMI, with no transition exception. That indication is ordinary-text information to the driver. B broadly forbids ETCS from providing any information during level transitions. The only compatibility story offered—blanking/freezing the display—depends on extra assumptions about what counts as 'information' and was not grounded by the pair text. So the strongest text-grounded relation is inconsistency/interference during the transition window.

## 4_8

- Gold class: `conflict`
- Predicted verdict: `incompatible`
- Confidence: `0.9624999999999999`
- R4: The driver shall acknowledge the level transitions, if requested from trackside. If the driver does not acknowledge after the transition the brake shall be applied. If the driver acknowledges afterwards, the brake can be released
- R8: ETCS shall not require any driver input for level transitions.
- Final reasoning: Skipped debate and arbitration because all four phase-1 agents produced the same verdict.

## 4_52

- Gold class: `conflict`
- Predicted verdict: `incompatible`
- Confidence: `0.975`
- R4: The driver shall acknowledge the level transitions, if requested from trackside. If the driver does not acknowledge after the transition the brake shall be applied. If the driver acknowledges afterwards, the brake can be released
- R52: ETCS shall not require the driver to acknowledge any level transitions, even if requested from trackside.
- Final reasoning: Skipped debate and arbitration because all four phase-1 agents produced the same verdict.

## 6_13

- Gold class: `conflict`
- Predicted verdict: `incompatible`
- Confidence: `1.0`
- R6: ETCS shall be compatible with existing national systems listed in the CCS TSI such that it does not interfere with the national systems and is not interfered with by the national systems.
- R13: ETCS shall not be compatible with any national systems listed in the CCS TSI.
- Final reasoning: Skipped debate and arbitration because all four phase-1 agents produced the same verdict.

## 6_58

- Gold class: `conflict`
- Predicted verdict: `incompatible`
- Confidence: `0.925`
- R6: ETCS shall be compatible with existing national systems listed in the CCS TSI such that it does not interfere with the national systems and is not interfered with by the national systems.
- R58: ETCS shall only be compatible with national systems listed in the CCS TSI if those systems are also equipped withETCS.
- Final reasoning: Skipped debate and arbitration because all four phase-1 agents produced the same verdict.

## 8_9

- Gold class: `conflict`
- Predicted verdict: `incompatible`
- Confidence: `0.87`
- R8: ETCS shall not require any driver input for level transitions.
- R9: If, as a result of an automatic transition, except for transitions to and from national Operation (STM), the responsibility for the driver increases, the ETCS shall seek an acknowledgement from the driver, whether the train is stationary or not.
- Final reasoning: Both requirements are anchored to ETCS level transitions, with B governing a subset of automatic transitions. A prohibits ETCS from requiring any driver input for level transitions. B says ETCS shall seek driver acknowledgement when an automatic transition increases driver responsibility (except STM). Under the ordinary meaning of "acknowledgement from the driver," this is driver input tied to the transition. That creates a text-grounded inconsistency for the overlapping cases. The non-blocking/optional reading is possible, but it depends on weakening "seek an acknowledgement" beyond its ordinary reading and is not clearly supported by the text.

## 8_47

- Gold class: `conflict`
- Predicted verdict: `incompatible`
- Confidence: `0.9624999999999999`
- R8: ETCS shall not require any driver input for level transitions.
- R47: The driver shall acknowledge the level transitions, if requested from trackside. If the driver does not acknowledgeafter the transition the brake shall be applied. If the driver acknowledges afterwards, the brake can be released
- Final reasoning: Skipped debate and arbitration because all four phase-1 agents produced the same verdict.

## 10_12

- Gold class: `conflict`
- Predicted verdict: `incompatible`
- Confidence: `0.975`
- R10: ETCS shall not be required to provide any track-to-train or train-to-track information via continuous transmissionmedia, i.e. radio.
- R12: Basic track to train and train to track information via continuous transmission media, i.e. radio. The train detection is provided by trackside.
- Final reasoning: Skipped debate and arbitration because all four phase-1 agents produced the same verdict.

## 13_64

- Gold class: `conflict`
- Predicted verdict: `incompatible`
- Confidence: `1.0`
- R13: ETCS shall not be compatible with any national systems listed in the CCS TSI.
- R64: ETCS shall be compatible with existing national systems listed in the CCS TSI such that it does not interfere withthe national systems and is not interfered with by the national systems.
- Final reasoning: Skipped debate and arbitration because all four phase-1 agents produced the same verdict.

## 15_52

- Gold class: `conflict`
- Predicted verdict: `incompatible`
- Confidence: `0.95`
- R15: If, as a result of an automatic transition, except for transitions to and from national Operation (STM), the responsibility for the driver increases, the ETCS shall seek an acknowledgement from the driver, whether th responsibility for the driver increases, the ETCS shall seek an acknowledgement from the driver, whether the train is stationary or not.
- R52: ETCS shall not require the driver to acknowledge any level transitions, even if requested from trackside.
- Final reasoning: Skipped debate and arbitration because all four phase-1 agents produced the same verdict.

## 18_37

- Gold class: `conflict`
- Predicted verdict: `incompatible`
- Confidence: `0.9875`
- R18: ETCS is required to be functional to a maximum train speed of 600 km/h.
- R37: ETCS shall only be functional up to a maximum train speed of 100 km/h.
- Final reasoning: Skipped debate and arbitration because all four phase-1 agents produced the same verdict.

## 18_38

- Gold class: `conflict`
- Predicted verdict: `incompatible`
- Confidence: `0.96`
- R18: ETCS is required to be functional to a maximum train speed of 600 km/h.
- R38: ETCS is required to be functional to a maximum train speed of 500 km/h.
- Final reasoning: Both requirements are anchored to the same target (ETCS) and the same constraint dimension (maximum train speed for required functionality). They prescribe different numeric maxima: 600 km/h vs 500 km/h. Under the ordinary meaning of “maximum,” these are mismatched bounds on the same property, which establishes a textual inconsistency even without proving implementation impossibility. The compatibility argument relies on treating the higher value as simply subsuming the lower, but that does not resolve the specification-level mismatch about what the required maximum is.

## 18_49

- Gold class: `conflict`
- Predicted verdict: `incompatible`
- Confidence: `0.96`
- R18: ETCS is required to be functional to a maximum train speed of 600 km/h.
- R49: ETCS is required to be functional to a maximum train speed of 500 km/h.
- Final reasoning: Both requirements are anchored to the same target (ETCS) and the same constraint dimension (maximum train speed for required functionality). They prescribe different numeric maxima: 600 km/h vs 500 km/h. Under the ordinary meaning of “maximum,” these are mismatched bounds on the same property, which establishes a textual inconsistency even without proving implementation impossibility. The compatibility argument relies on treating the higher value as simply subsuming the lower, but that does not resolve the specification-level mismatch about what the required maximum is.

## 19_45

- Gold class: `conflict`
- Predicted verdict: `incompatible`
- Confidence: `0.9875`
- R19: ETCS shall not be able to supervise shunting movements.
- R45: ETCS shall be able to supervise train and shunting movements.
- Final reasoning: Skipped debate and arbitration because all four phase-1 agents produced the same verdict.

## 19_53

- Gold class: `conflict`
- Predicted verdict: `incompatible`
- Confidence: `0.9875`
- R19: ETCS shall not be able to supervise shunting movements.
- R53: ETCS shall be able to supervise train and shunting movements.
- Final reasoning: Skipped debate and arbitration because all four phase-1 agents produced the same verdict.

## 23_42

- Gold class: `conflict`
- Predicted verdict: `incompatible`
- Confidence: `0.94`
- R23: ETCS shall provide the driver with information to allow him to drive the train safely.
- R42: ETCS shall not provide any information to the driver during level transitions.
- Final reasoning: Both requirements are anchored to the same target and capability: ETCS providing information to the driver. A imposes a positive obligation to provide information so the driver can drive safely. B imposes an absolute negative obligation to provide no information during level transitions. Since level transitions are a driving condition covered by the ordinary meaning of driving the train safely, B directly interferes with and is inconsistent with A over that condition. The compatibility story depended on a speculative time-split that does not remove the text-grounded conflict.

## 23_61

- Gold class: `conflict`
- Predicted verdict: `incompatible`
- Confidence: `0.97`
- R23: ETCS shall provide the driver with information to allow him to drive the train safely.
- R61: ETCS shall only provide the driver with information to allow him to drive the train safely if the train speed is below400 km/h.
- Final reasoning: Both requirements target the same subject, action, and information: ETCS providing the driver with safe-driving information. A is unconditional. B adds an explicit exclusivity constraint: ETCS shall only provide that information if speed is below 400 km/h. Thus, at speeds >=400 km/h, B forbids the provision that A still requires. This is a text-grounded inconsistency on the same capability and operating condition, and it also makes joint satisfaction impossible for that speed range. The feasibility-based coexistence path depended on extra assumptions about operation above 400 km/h that are not stated in the pair.

## 24_42

- Gold class: `conflict`
- Predicted verdict: `incompatible`
- Confidence: `0.92`
- R24: Default values shall be harmonised values, permanently stored in all ERTMS/ETCS on board equipment. ETCS shallprovide the driver with information to allow him to drive the train safely.
- R42: ETCS shall not provide any information to the driver during level transitions.
- Final reasoning: The pair is textually anchored to the same target and capability: ETCS providing information to the driver. Requirement A imposes an unqualified obligation that ETCS shall provide the driver with information needed for safe driving. Requirement B imposes an absolute prohibition on providing any information to the driver during level transitions. That prohibition directly interferes with, and is inconsistent with, A over the shared operating condition of level transitions. The earlier compatible reading depended on an unsupported scope/time split and was withdrawn on cross-examination. No textual exception in A excludes level transitions, so the strongest surviving evidence establishes incompatibility.

## 24_61

- Gold class: `conflict`
- Predicted verdict: `incompatible`
- Confidence: `0.97`
- R24: Default values shall be harmonised values, permanently stored in all ERTMS/ETCS on board equipment. ETCS shallprovide the driver with information to allow him to drive the train safely.
- R61: ETCS shall only provide the driver with information to allow him to drive the train safely if the train speed is below400 km/h.
- Final reasoning: The pair is textually anchored to the same capability: ETCS providing the driver with information for safe driving. In A, that obligation is unconditional: ETCS shall provide the information. In B, 'shall only provide ... if the train speed is below 400 km/h' makes speed < 400 a necessary condition, which forbids provision at 400 km/h or above. That directly conflicts with A’s unrestricted mandate over the same function and operating condition. The default-values sentence in A does not remove this conflict; it is separate and non-curative. The strongest surviving evidence therefore establishes a direct inconsistency, making the pair incompatible.

## 25_45

- Gold class: `conflict`
- Predicted verdict: `incompatible`
- Confidence: `1.0`
- R25: ETCS shall not be able to supervise train or shunting movements.
- R45: ETCS shall be able to supervise train and shunting movements.
- Final reasoning: Skipped debate and arbitration because all four phase-1 agents produced the same verdict.

## 25_53

- Gold class: `conflict`
- Predicted verdict: `incompatible`
- Confidence: `1.0`
- R25: ETCS shall not be able to supervise train or shunting movements.
- R53: ETCS shall be able to supervise train and shunting movements.
- Final reasoning: Skipped debate and arbitration because all four phase-1 agents produced the same verdict.

## 28_37

- Gold class: `conflict`
- Predicted verdict: `incompatible`
- Confidence: `0.97`
- R28: ETCS shall allow for manual speed control by the driver at all times, regardless of the maximum train speed.
- R37: ETCS shall only be functional up to a maximum train speed of 100 km/h.
- Final reasoning: Both requirements are anchored to the same target (ETCS) and the same operating dimension (train speed). A requires ETCS to allow driver manual speed control "at all times" and "regardless of the maximum train speed," which textually includes speeds above 100 km/h. B says ETCS shall only be functional up to 100 km/h. Above 100 km/h, B withdraws ETCS functionality precisely where A still requires an ETCS-provided capability. The rejected compatibility path depended on an unsupported split between driver control and ETCS, but A explicitly makes this an ETCS function. This establishes a text-grounded interference and inconsistency.

## 30_37

- Gold class: `conflict`
- Predicted verdict: `incompatible`
- Confidence: `0.91`
- R30: If an ETCS equipped train passes a level transition to one or more levels for which it is not equipped, ETCS shallinitiate a brake application.
- R37: ETCS shall only be functional up to a maximum train speed of 100 km/h.
- Final reasoning: Both requirements are anchored to ETCS behavior under operating conditions. A requires ETCS to initiate braking whenever an equipped train passes a transition to unequipped level(s), with no speed exception. B sets a hard speed envelope: ETCS shall only be functional up to 100 km/h, which textually excludes ETCS functionality above that speed. Therefore, for any such transition event occurring above 100 km/h, A requires ETCS to act while B requires ETCS not to be functional. That is a text-grounded inconsistency/impossible joint satisfaction on the same system capability, without needing a speculative scope split.

## 31_37

- Gold class: `conflict`
- Predicted verdict: `incompatible`
- Confidence: `0.82`
- R31: If an ETCS equipped train passes a level transition to a line fitted with more than one level, the onboard shallswitch to the highest level, according to the priority given by trackside, for which it is equipped.
- R37: ETCS shall only be functional up to a maximum train speed of 100 km/h.
- Final reasoning: The pair is anchored to the same target: ETCS onboard behavior. Requirement A unconditionally requires the onboard to switch to the highest ETCS level whenever the train passes the specified level transition; it gives no speed exception. Requirement B says ETCS shall only be functional up to 100 km/h. Since level switching is itself an ETCS function, B withdraws the functionality A requires for any qualifying transition above 100 km/h. That is a text-grounded interference/inconsistency on the same capability, not merely a speculative coexistence issue.

## 31_43

- Gold class: `conflict`
- Predicted verdict: `incompatible`
- Confidence: `0.9624999999999999`
- R31: If an ETCS equipped train passes a level transition to a line fitted with more than one level, the onboard shallswitch to the highest level, according to the priority given by trackside, for which it is equipped.
- R43: The ETCS onboard equipment shall automatically switch to the lowest level available on a line, even if it is notequipped for that level.
- Final reasoning: Skipped debate and arbitration because all four phase-1 agents produced the same verdict.

## 32_42

- Gold class: `conflict`
- Predicted verdict: `incompatible`
- Confidence: `0.925`
- R32: The current operational status shall be indicated to the driver on the DMI
- R42: ETCS shall not provide any information to the driver during level transitions.
- Final reasoning: Skipped debate and arbitration because all four phase-1 agents produced the same verdict.

## 33_37

- Gold class: `conflict`
- Predicted verdict: `incompatible`
- Confidence: `0.91`
- R33: If an ETCS equipped train passes a level transition to one or more levels for which it is not equipped, ETCS shallinitiate a brake application.
- R37: ETCS shall only be functional up to a maximum train speed of 100 km/h.
- Final reasoning: Both requirements are anchored to ETCS behavior under operating conditions. A requires ETCS to initiate braking whenever an equipped train passes a transition to unequipped level(s), with no speed exception. B sets a hard speed envelope: ETCS shall only be functional up to 100 km/h, which textually excludes ETCS functionality above that speed. Therefore, for any such transition event occurring above 100 km/h, A requires ETCS to act while B requires ETCS not to be functional. That is a text-grounded inconsistency/impossible joint satisfaction on the same system capability, without needing a speculative scope split.

## 37_38

- Gold class: `conflict`
- Predicted verdict: `incompatible`
- Confidence: `0.9824999999999999`
- R37: ETCS shall only be functional up to a maximum train speed of 100 km/h.
- R38: ETCS is required to be functional to a maximum train speed of 500 km/h.
- Final reasoning: Skipped debate and arbitration because all four phase-1 agents produced the same verdict.

## 37_49

- Gold class: `conflict`
- Predicted verdict: `incompatible`
- Confidence: `0.9824999999999999`
- R37: ETCS shall only be functional up to a maximum train speed of 100 km/h.
- R49: ETCS is required to be functional to a maximum train speed of 500 km/h.
- Final reasoning: Skipped debate and arbitration because all four phase-1 agents produced the same verdict.

## 42_59

- Gold class: `conflict`
- Predicted verdict: `incompatible`
- Confidence: `0.91`
- R42: ETCS shall not provide any information to the driver during level transitions.
- R59: The current application level shall be indicated on the DMI.
- Final reasoning: The pair overlaps on the same information channel and operating condition: ETCS/DMI information shown to the driver during level transitions. A requires the current application level to be indicated on the DMI, with no transition exception. That indication is ordinary-text information to the driver. B broadly forbids ETCS from providing any information during level transitions. The only compatibility story offered—blanking/freezing the display—depends on extra assumptions about what counts as 'information' and was not grounded by the pair text. So the strongest text-grounded relation is inconsistency/interference during the transition window.

## 43_46

- Gold class: `conflict`
- Predicted verdict: `incompatible`
- Confidence: `0.95`
- R43: The ETCS onboard equipment shall automatically switch to the lowest level available on a line, even if it is notequipped for that level.
- R46: If an ETCS equipped train passes a level transition to a line fitted with more than one level, the onboard shallswitch to the highest level, according to the priority given by trackside, for which it is equipped
- Final reasoning: Both requirements are anchored to the same target and function: ETCS onboard automatic level selection for a line/line transition. Requirement B is a specific case of entering a line with more than one level. In that overlap, A requires switching to the lowest available level, and explicitly says this holds even if the train is not equipped for that level; B requires switching to the highest level for which it is equipped. Those prescriptions conflict on the same selection decision, establishing a direct inconsistency/interference. The compatibility rebuttal misreads A as applying only when unequipped, but A is unconditional and only stresses that lack of equipment does not block the switch.

## 44_56

- Gold class: `conflict`
- Predicted verdict: `incompatible`
- Confidence: `0.9875`
- R44: Basic track to train information via intermittent transmission media, e.g. balises. This information can besupported by infill, transmitted via balise, loop or radio.
- R56: Basic track to train information shall only be provided via radio and not via balises.
- Final reasoning: Skipped debate and arbitration because all four phase-1 agents produced the same verdict.

## 47_52

- Gold class: `conflict`
- Predicted verdict: `incompatible`
- Confidence: `0.975`
- R47: The driver shall acknowledge the level transitions, if requested from trackside. If the driver does not acknowledgeafter the transition the brake shall be applied. If the driver acknowledges afterwards, the brake can be released
- R52: ETCS shall not require the driver to acknowledge any level transitions, even if requested from trackside.
- Final reasoning: Skipped debate and arbitration because all four phase-1 agents produced the same verdict.

## 55_56

- Gold class: `conflict`
- Predicted verdict: `incompatible`
- Confidence: `0.9875`
- R55: Basic track to train information via intermittent transmission media, e.g. balises. This information can besupported by infill, transmitted via balise, loop or radio.
- R56: Basic track to train information shall only be provided via radio and not via balises.
- Final reasoning: Skipped debate and arbitration because all four phase-1 agents produced the same verdict.

## 58_64

- Gold class: `conflict`
- Predicted verdict: `incompatible`
- Confidence: `0.925`
- R58: ETCS shall only be compatible with national systems listed in the CCS TSI if those systems are also equipped withETCS.
- R64: ETCS shall be compatible with existing national systems listed in the CCS TSI such that it does not interfere withthe national systems and is not interfered with by the national systems.
- Final reasoning: Skipped debate and arbitration because all four phase-1 agents produced the same verdict.
