# False Positive Conflicts

Total pairs: **26**

## 3_44

- Gold class: `not labeled`
- Predicted verdict: `incompatible`
- Confidence: `0.88`
- R3: Basic track to train and train to track information via continuous transmission media, i.e. radio. The train detection is provided by trackside
- R44: Basic track to train information via intermittent transmission media, e.g. balises. This information can besupported by infill, transmitted via balise, loop or radio.
- Final reasoning: The pair is textually anchored to the same target: “basic track to train information.” Requirement A prescribes that this basic information is provided via continuous transmission media, i.e. radio. Requirement B prescribes that the same basic track-to-train information is via intermittent transmission media, e.g. balises, with optional infill support. That is a direct mismatch on the same constraint dimension (transmission mode/media). A compatibility story requires an unstated assumption that the same basic information may simultaneously be specified through two different baseline media or split across architectures, which the text does not ground. The strongest surviving evidence therefore establishes inconsistency.

## 3_55

- Gold class: `not labeled`
- Predicted verdict: `incompatible`
- Confidence: `0.88`
- R3: Basic track to train and train to track information via continuous transmission media, i.e. radio. The train detection is provided by trackside
- R55: Basic track to train information via intermittent transmission media, e.g. balises. This information can besupported by infill, transmitted via balise, loop or radio.
- Final reasoning: The pair is textually anchored to the same target: “basic track to train information.” Requirement A prescribes that this basic information is provided via continuous transmission media, i.e. radio. Requirement B prescribes that the same basic track-to-train information is via intermittent transmission media, e.g. balises, with optional infill support. That is a direct mismatch on the same constraint dimension (transmission mode/media). A compatibility story requires an unstated assumption that the same basic information may simultaneously be specified through two different baseline media or split across architectures, which the text does not ground. The strongest surviving evidence therefore establishes inconsistency.

## 4_28

- Gold class: `not labeled`
- Predicted verdict: `incompatible`
- Confidence: `0.81`
- R4: The driver shall acknowledge the level transitions, if requested from trackside. If the driver does not acknowledge after the transition the brake shall be applied. If the driver acknowledges afterwards, the brake can be released
- R28: ETCS shall allow for manual speed control by the driver at all times, regardless of the maximum train speed.
- Final reasoning: The pair is anchored to the same operational capability: control of train speed during operation. A requires ETCS to apply the brake if the driver does not acknowledge a level transition request; that is a mandatory automatic intervention affecting speed control. B requires ETCS to allow manual speed control by the driver "at all times." The strongest text-grounded reading is interference: in the no-acknowledgment state mandated by A, automatic braking constrains or overrides the driver’s speed control, which conflicts with B’s uninterrupted availability requirement. The surviving compatibility argument depends on weakening the explicit phrase "at all times," which is not supported by the pair text.

## 4_42

- Gold class: `not labeled`
- Predicted verdict: `incompatible`
- Confidence: `0.95`
- R4: The driver shall acknowledge the level transitions, if requested from trackside. If the driver does not acknowledge after the transition the brake shall be applied. If the driver acknowledges afterwards, the brake can be released
- R42: ETCS shall not provide any information to the driver during level transitions.
- Final reasoning: Skipped debate and arbitration because all four phase-1 agents produced the same verdict.

## 5_42

- Gold class: `not labeled`
- Predicted verdict: `incompatible`
- Confidence: `0.95`
- R5: For transitions to and from national Operation (STM) the ETCS shall request, an acknowledgement by the driver.
- R42: ETCS shall not provide any information to the driver during level transitions.
- Final reasoning: Skipped debate and arbitration because all four phase-1 agents produced the same verdict.

## 8_11

- Gold class: `not labeled`
- Predicted verdict: `incompatible`
- Confidence: `0.925`
- R8: ETCS shall not require any driver input for level transitions.
- R11: In case the transition has to be acknowledged and the driver fails to acknowledge as required, the ETCS shall initiate a brake application
- Final reasoning: Skipped debate and arbitration because all four phase-1 agents produced the same verdict.

## 8_15

- Gold class: `not labeled`
- Predicted verdict: `incompatible`
- Confidence: `0.95`
- R8: ETCS shall not require any driver input for level transitions.
- R15: If, as a result of an automatic transition, except for transitions to and from national Operation (STM), the responsibility for the driver increases, the ETCS shall seek an acknowledgement from the driver, whether th responsibility for the driver increases, the ETCS shall seek an acknowledgement from the driver, whether the train is stationary or not.
- Final reasoning: Skipped debate and arbitration because all four phase-1 agents produced the same verdict.

## 8_20

- Gold class: `not labeled`
- Predicted verdict: `incompatible`
- Confidence: `0.925`
- R8: ETCS shall not require any driver input for level transitions.
- R20: In case the transition has to be acknowledged and the driver fails to acknowledge as required, the ETCS shallinitiate a brake application
- Final reasoning: Skipped debate and arbitration because all four phase-1 agents produced the same verdict.

## 8_34

- Gold class: `not labeled`
- Predicted verdict: `incompatible`
- Confidence: `0.95`
- R8: ETCS shall not require any driver input for level transitions.
- R34: transitions which occur while the train is stationary, shall be initiated automatically or manually as appropriate.
- Final reasoning: The pair is anchored to the same target: ETCS level transitions, with B addressing the stationary subset. A sets a blanket constraint that level transitions shall not require any driver input. B says stationary transitions shall be initiated automatically or manually as appropriate; in the pair text, the ordinary reading of “manually” is human/driver initiation, and no wording supports a different actor. That creates a direct inconsistency on stationary transitions: A forbids required driver input for any level transition, while B permits/depends on manual initiation where appropriate. The surviving conflict is text-grounded and does not rely on a speculative scope split.

## 8_48

- Gold class: `not labeled`
- Predicted verdict: `incompatible`
- Confidence: `0.95`
- R8: ETCS shall not require any driver input for level transitions.
- R48: transitions which occur while the train is stationary, shall be initiated automatically or manually as appropriate.
- Final reasoning: The pair is anchored to the same target: ETCS level transitions, with B addressing the stationary subset. A sets a blanket constraint that level transitions shall not require any driver input. B says stationary transitions shall be initiated automatically or manually as appropriate; in the pair text, the ordinary reading of “manually” is human/driver initiation, and no wording supports a different actor. That creates a direct inconsistency on stationary transitions: A forbids required driver input for any level transition, while B permits/depends on manual initiation where appropriate. The surviving conflict is text-grounded and does not rely on a speculative scope split.

## 10_56

- Gold class: `not labeled`
- Predicted verdict: `incompatible`
- Confidence: `0.9624999999999999`
- R10: ETCS shall not be required to provide any track-to-train or train-to-track information via continuous transmissionmedia, i.e. radio.
- R56: Basic track to train information shall only be provided via radio and not via balises.
- Final reasoning: Skipped debate and arbitration because all four phase-1 agents produced the same verdict.

## 11_25

- Gold class: `not labeled`
- Predicted verdict: `incompatible`
- Confidence: `0.95`
- R11: In case the transition has to be acknowledged and the driver fails to acknowledge as required, the ETCS shall initiate a brake application
- R25: ETCS shall not be able to supervise train or shunting movements.
- Final reasoning: Skipped debate and arbitration because all four phase-1 agents produced the same verdict.

## 11_28

- Gold class: `not labeled`
- Predicted verdict: `incompatible`
- Confidence: `0.84`
- R11: In case the transition has to be acknowledged and the driver fails to acknowledge as required, the ETCS shall initiate a brake application
- R28: ETCS shall allow for manual speed control by the driver at all times, regardless of the maximum train speed.
- Final reasoning: Both requirements are anchored to ETCS control over train speed in the same operational context. A requires ETCS to initiate braking when a required acknowledgement is missed. B requires ETCS to allow manual speed control by the driver at all times. The strongest text-grounded reading is that an ETCS-initiated brake application interferes with, and thus undermines, uninterrupted driver manual speed control in that condition. The compatibility arguments depend on an unstated assumption that manual control remains meaningfully available during the safety brake override, but the pair text does not provide that exception.

## 15_37

- Gold class: `not labeled`
- Predicted verdict: `incompatible`
- Confidence: `0.78`
- R15: If, as a result of an automatic transition, except for transitions to and from national Operation (STM), the responsibility for the driver increases, the ETCS shall seek an acknowledgement from the driver, whether th responsibility for the driver increases, the ETCS shall seek an acknowledgement from the driver, whether the train is stationary or not.
- R37: ETCS shall only be functional up to a maximum train speed of 100 km/h.
- Final reasoning: Both requirements target ETCS behavior. A requires ETCS itself to seek driver acknowledgement whenever the specified automatic transition increases driver responsibility, with no speed exception and explicitly regardless of the train being stationary or moving. B says ETCS shall only be functional up to 100 km/h, which textually means ETCS is not functional above that speed. That creates a direct interference/inconsistency for any qualifying transition occurring above 100 km/h: A requires ETCS action there, while B removes ETCS functionality there. The compatibility claim depends on an unstated operating-condition restriction for A, which the pair does not provide.

## 18_25

- Gold class: `not labeled`
- Predicted verdict: `incompatible`
- Confidence: `0.95`
- R18: ETCS is required to be functional to a maximum train speed of 600 km/h.
- R25: ETCS shall not be able to supervise train or shunting movements.
- Final reasoning: Skipped debate and arbitration because all four phase-1 agents produced the same verdict.

## 20_25

- Gold class: `not labeled`
- Predicted verdict: `incompatible`
- Confidence: `0.95`
- R20: In case the transition has to be acknowledged and the driver fails to acknowledge as required, the ETCS shallinitiate a brake application
- R25: ETCS shall not be able to supervise train or shunting movements.
- Final reasoning: Skipped debate and arbitration because all four phase-1 agents produced the same verdict.

## 20_28

- Gold class: `not labeled`
- Predicted verdict: `incompatible`
- Confidence: `0.84`
- R20: In case the transition has to be acknowledged and the driver fails to acknowledge as required, the ETCS shallinitiate a brake application
- R28: ETCS shall allow for manual speed control by the driver at all times, regardless of the maximum train speed.
- Final reasoning: Both requirements are anchored to ETCS control over train speed in the same operational context. A requires ETCS to initiate braking when a required acknowledgement is missed. B requires ETCS to allow manual speed control by the driver at all times. The strongest text-grounded reading is that an ETCS-initiated brake application interferes with, and thus undermines, uninterrupted driver manual speed control in that condition. The compatibility arguments depend on an unstated assumption that manual control remains meaningfully available during the safety brake override, but the pair text does not provide that exception.

## 25_30

- Gold class: `not labeled`
- Predicted verdict: `incompatible`
- Confidence: `0.88`
- R25: ETCS shall not be able to supervise train or shunting movements.
- R30: If an ETCS equipped train passes a level transition to one or more levels for which it is not equipped, ETCS shallinitiate a brake application.
- Final reasoning: Both requirements are anchored to ETCS behavior over train movement. A broadly forbids ETCS from being able to supervise train or shunting movements. B requires ETCS, upon a specific movement-related condition, to detect that condition and initiate a brake application. Initiating braking in response to a train movement event is textually a form of movement supervision/control under the ordinary meaning of the words, so B requires a capability that A denies. This establishes at least inconsistency, and effectively impossible joint satisfaction for the same ETCS capability.

## 25_33

- Gold class: `not labeled`
- Predicted verdict: `incompatible`
- Confidence: `0.88`
- R25: ETCS shall not be able to supervise train or shunting movements.
- R33: If an ETCS equipped train passes a level transition to one or more levels for which it is not equipped, ETCS shallinitiate a brake application.
- Final reasoning: Both requirements are anchored to ETCS behavior over train movement. A broadly forbids ETCS from being able to supervise train or shunting movements. B requires ETCS, upon a specific movement-related condition, to detect that condition and initiate a brake application. Initiating braking in response to a train movement event is textually a form of movement supervision/control under the ordinary meaning of the words, so B requires a capability that A denies. This establishes at least inconsistency, and effectively impossible joint satisfaction for the same ETCS capability.

## 28_30

- Gold class: `not labeled`
- Predicted verdict: `incompatible`
- Confidence: `0.91`
- R28: ETCS shall allow for manual speed control by the driver at all times, regardless of the maximum train speed.
- R30: If an ETCS equipped train passes a level transition to one or more levels for which it is not equipped, ETCS shallinitiate a brake application.
- Final reasoning: Both requirements are anchored to the same target: control of train speed under ETCS. A requires ETCS to allow driver manual speed control "at all times," with no exception stated beyond maximum speed. B requires ETCS itself to initiate a brake application in a specific condition. That automatic braking interferes with and constrains the driver’s continuous manual speed-control capability during that event. The compatibility arguments depend on adding an unstated normal/fault or operational-envelope limitation to A, which the text does not support. The strongest text-grounded relation is interference, with a related inconsistency between A’s unqualified continuity and B’s mandated automatic takeover.

## 28_33

- Gold class: `not labeled`
- Predicted verdict: `incompatible`
- Confidence: `0.91`
- R28: ETCS shall allow for manual speed control by the driver at all times, regardless of the maximum train speed.
- R33: If an ETCS equipped train passes a level transition to one or more levels for which it is not equipped, ETCS shallinitiate a brake application.
- Final reasoning: Both requirements are anchored to the same target: control of train speed under ETCS. A requires ETCS to allow driver manual speed control "at all times," with no exception stated beyond maximum speed. B requires ETCS itself to initiate a brake application in a specific condition. That automatic braking interferes with and constrains the driver’s continuous manual speed-control capability during that event. The compatibility arguments depend on adding an unstated normal/fault or operational-envelope limitation to A, which the text does not support. The strongest text-grounded relation is interference, with a related inconsistency between A’s unqualified continuity and B’s mandated automatic takeover.

## 28_47

- Gold class: `not labeled`
- Predicted verdict: `incompatible`
- Confidence: `0.81`
- R28: ETCS shall allow for manual speed control by the driver at all times, regardless of the maximum train speed.
- R47: The driver shall acknowledge the level transitions, if requested from trackside. If the driver does not acknowledgeafter the transition the brake shall be applied. If the driver acknowledges afterwards, the brake can be released
- Final reasoning: The pair is anchored to the same operational capability: control of train speed during operation. A requires ETCS to apply the brake if the driver does not acknowledge a level transition request; that is a mandatory automatic intervention affecting speed control. B requires ETCS to allow manual speed control by the driver "at all times." The strongest text-grounded reading is interference: in the no-acknowledgment state mandated by A, automatic braking constrains or overrides the driver’s speed control, which conflicts with B’s uninterrupted availability requirement. The surviving compatibility argument depends on weakening the explicit phrase "at all times," which is not supported by the pair text.

## 30_46

- Gold class: `not labeled`
- Predicted verdict: `incompatible`
- Confidence: `0.83`
- R30: If an ETCS equipped train passes a level transition to one or more levels for which it is not equipped, ETCS shallinitiate a brake application.
- R46: If an ETCS equipped train passes a level transition to a line fitted with more than one level, the onboard shallswitch to the highest level, according to the priority given by trackside, for which it is equipped
- Final reasoning: Both requirements are anchored to the same event: an ETCS-equipped train passing a level transition involving multiple possible levels. Requirement A textually triggers when the transition includes "one or more levels for which it is not equipped"; Requirement B triggers when the line has more than one level and the train is equipped for at least one, requiring a switch to the highest equipped level. In the mixed case (equipped for some offered levels but not others), both conditions are satisfied. A requires brake application, while B requires switching level, creating a text-grounded operational inconsistency/interference. The compatible reading survives only by reinterpreting A as meaning "equipped for none," which the pair text does not state.

## 33_46

- Gold class: `not labeled`
- Predicted verdict: `incompatible`
- Confidence: `0.83`
- R33: If an ETCS equipped train passes a level transition to one or more levels for which it is not equipped, ETCS shallinitiate a brake application.
- R46: If an ETCS equipped train passes a level transition to a line fitted with more than one level, the onboard shallswitch to the highest level, according to the priority given by trackside, for which it is equipped
- Final reasoning: Both requirements are anchored to the same event: an ETCS-equipped train passing a level transition involving multiple possible levels. Requirement A textually triggers when the transition includes "one or more levels for which it is not equipped"; Requirement B triggers when the line has more than one level and the train is equipped for at least one, requiring a switch to the highest equipped level. In the mixed case (equipped for some offered levels but not others), both conditions are satisfied. A requires brake application, while B requires switching level, creating a text-grounded operational inconsistency/interference. The compatible reading survives only by reinterpreting A as meaning "equipped for none," which the pair text does not state.

## 42_47

- Gold class: `not labeled`
- Predicted verdict: `incompatible`
- Confidence: `0.95`
- R42: ETCS shall not provide any information to the driver during level transitions.
- R47: The driver shall acknowledge the level transitions, if requested from trackside. If the driver does not acknowledgeafter the transition the brake shall be applied. If the driver acknowledges afterwards, the brake can be released
- Final reasoning: Skipped debate and arbitration because all four phase-1 agents produced the same verdict.

## 42_50

- Gold class: `not labeled`
- Predicted verdict: `incompatible`
- Confidence: `0.95`
- R42: ETCS shall not provide any information to the driver during level transitions.
- R50: For transitions to and from national Operation (STM) the ETCS shall request, an acknowledgement by the driver.
- Final reasoning: Skipped debate and arbitration because all four phase-1 agents produced the same verdict.
