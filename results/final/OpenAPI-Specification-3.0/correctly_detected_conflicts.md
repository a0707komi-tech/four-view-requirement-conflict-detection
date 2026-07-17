# Correctly Detected Conflicts

Total pairs: **20**

## 1_52

- Gold class: `conflict`
- Predicted verdict: `incompatible`
- Confidence: `0.89`
- R1: All Operations MUST include the extension field x-category for annotating business domain classification; all Operations MUST also include the extension field x-category for annotating security audit classification.
- R52: Patterned fields MUST have unique names within their containing object.
- Final reasoning: The pair is anchored to the same containing Operation object and its field names. Requirement A twice mandates inclusion of the extension field named `x-category`, first for business domain classification and also for security audit classification. The plain reading of `also include the extension field x-category` adds a second required inclusion of the same field name in the same object. Requirement B requires patterned fields to have unique names within their containing object. That creates a direct inconsistency, and thus impossible joint satisfaction, if A requires two `x-category` fields in one Operation object. The main compatibility argument depends on reinterpreting A as one shared field serving both purposes, which is not clearly supported by the text.

## 6_48

- Gold class: `conflict`
- Predicted verdict: `incompatible`
- Confidence: `1.0`
- R6: All platform service OpenAPI documents MUST define the enterprise observability metadata as OpenAPI Specification Extension fields named exactly monitor.sla, monitor.owner, and monitor.tier. These field names are hardcoded in the observability platform's schema parser and MUST NOT be changed.
- R48: Each Specification Extension field name MUST begin with x-.
- Final reasoning: Skipped debate and arbitration because all four phase-1 agents produced the same verdict.

## 8_19

- Gold class: `conflict`
- Predicted verdict: `incompatible`
- Confidence: `0.9875`
- R8: OpenAPI documents that provide an Info Object termsOfService field MUST encode that field as a Markdown string.
- R19: OpenAPI documents that provide an Info Object termsOfService field MUST encode that field as a URL.
- Final reasoning: Skipped debate and arbitration because all four phase-1 agents produced the same verdict.

## 8_29

- Gold class: `conflict`
- Predicted verdict: `incompatible`
- Confidence: `0.995`
- R8: OpenAPI documents that provide an Info Object termsOfService field MUST encode that field as a Markdown string.
- R29: OpenAPI documents that provide an Info Object termsOfService field MUST encode that field as plain text.
- Final reasoning: Skipped debate and arbitration because all four phase-1 agents produced the same verdict.

## 10_54

- Gold class: `conflict`
- Predicted verdict: `incompatible`
- Confidence: `0.9624999999999999`
- R10: When an Operation Object defines a requestBody for an HTTP GET method, consumers MUST process and transmit that requestBody as the structured query payload.
- R54: When an Operation Object defines requestBody for an HTTP method whose request-body semantics are vague in the HTTP specification, consumers SHALL ignore that requestBody.
- Final reasoning: Skipped debate and arbitration because all four phase-1 agents produced the same verdict.

## 14_58

- Gold class: `conflict`
- Predicted verdict: `incompatible`
- Confidence: `1.0`
- R14: When a Security Requirement Object contains multiple schemes, a request SHALL be authorized if any one of those schemes is successfully validated.
- R58: Security Requirement Objects that contain multiple schemes require all of those schemes to be satisfied before a request is authorized.
- Final reasoning: Skipped debate and arbitration because all four phase-1 agents produced the same verdict.

## 16_48

- Gold class: `conflict`
- Predicted verdict: `incompatible`
- Confidence: `1.0`
- R16: All platform service OpenAPI documents MUST define the enterprise observability metadata as OpenAPI Specification Extension fields named exactly monitor.sla, monitor.owner, and monitor.tier. These field names are hardcoded in the observability platform's schema parser and MUST NOT be changed.
- R48: Each Specification Extension field name MUST begin with x-.
- Final reasoning: Skipped debate and arbitration because all four phase-1 agents produced the same verdict.

## 18_52

- Gold class: `conflict`
- Predicted verdict: `incompatible`
- Confidence: `0.89`
- R18: All Operations MUST include the extension field x-category for annotating business domain classification; all Operations MUST also include the extension field x-category for annotating security audit classification.
- R52: Patterned fields MUST have unique names within their containing object.
- Final reasoning: The pair is anchored to the same containing Operation object and its field names. Requirement A twice mandates inclusion of the extension field named `x-category`, first for business domain classification and also for security audit classification. The plain reading of `also include the extension field x-category` adds a second required inclusion of the same field name in the same object. Requirement B requires patterned fields to have unique names within their containing object. That creates a direct inconsistency, and thus impossible joint satisfaction, if A requires two `x-category` fields in one Operation object. The main compatibility argument depends on reinterpreting A as one shared field serving both purposes, which is not clearly supported by the text.

## 19_29

- Gold class: `conflict`
- Predicted verdict: `incompatible`
- Confidence: `1.0`
- R19: OpenAPI documents that provide an Info Object termsOfService field MUST encode that field as a URL.
- R29: OpenAPI documents that provide an Info Object termsOfService field MUST encode that field as plain text.
- Final reasoning: Skipped debate and arbitration because all four phase-1 agents produced the same verdict.

## 19_32

- Gold class: `conflict`
- Predicted verdict: `incompatible`
- Confidence: `0.9875`
- R19: OpenAPI documents that provide an Info Object termsOfService field MUST encode that field as a URL.
- R32: OpenAPI documents that provide an Info Object termsOfService field MUST encode that field as a Markdown string.
- Final reasoning: Skipped debate and arbitration because all four phase-1 agents produced the same verdict.

## 20_21

- Gold class: `conflict`
- Predicted verdict: `incompatible`
- Confidence: `0.9875`
- R20: The version field in the Info Object MUST reflect the current deployed version of the API implementation, and MUST be updated whenever a new version of the API is released to production.
- R21: The Info Object version field MUST represent the version of the OpenAPI document rather than the OpenAPI Specification version or the API implementation version.
- Final reasoning: Skipped debate and arbitration because all four phase-1 agents produced the same verdict.

## 23_33

- Gold class: `conflict`
- Predicted verdict: `incompatible`
- Confidence: `1.0`
- R23: Each field name in the Paths Object MUST begin with a forward slash (/).
- R33: Each field name in the Paths Object MUST begin with a backslash (\).
- Final reasoning: Skipped debate and arbitration because all four phase-1 agents produced the same verdict.

## 23_38

- Gold class: `conflict`
- Predicted verdict: `incompatible`
- Confidence: `1.0`
- R23: Each field name in the Paths Object MUST begin with a forward slash (/).
- R38: Each field name in the Paths Object MUST NOT begin with a forward slash (/).
- Final reasoning: Skipped debate and arbitration because all four phase-1 agents produced the same verdict.

## 23_43

- Gold class: `conflict`
- Predicted verdict: `incompatible`
- Confidence: `1.0`
- R23: Each field name in the Paths Object MUST begin with a forward slash (/).
- R43: Each field name in the Paths Object MUST begin with a backslash (\).
- Final reasoning: Skipped debate and arbitration because all four phase-1 agents produced the same verdict.

## 23_55

- Gold class: `conflict`
- Predicted verdict: `incompatible`
- Confidence: `1.0`
- R23: Each field name in the Paths Object MUST begin with a forward slash (/).
- R55: Each field name in the Paths Object MUST begin with an alphanumeric character.
- Final reasoning: Skipped debate and arbitration because all four phase-1 agents produced the same verdict.

## 27_31

- Gold class: `conflict`
- Predicted verdict: `incompatible`
- Confidence: `0.9875`
- R27: When an API parameter is renamed between versions, the corresponding Path Item Object or Operation Object MUST include both the original parameter declaration and the renamed parameter declaration during the transition period, and both declarations MUST use the same name at the same location, so that existing clients require no modification to remain functional.
- R31: Path Item Objects and Operation Objects MUST NOT include duplicated parameters; a unique parameter is defined by the combination of its name and location.
- Final reasoning: Skipped debate and arbitration because all four phase-1 agents produced the same verdict.

## 29_30

- Gold class: `conflict`
- Predicted verdict: `incompatible`
- Confidence: `1.0`
- R29: OpenAPI documents that provide an Info Object termsOfService field MUST encode that field as plain text.
- R30: OpenAPI documents that provide an Info Object termsOfService field MUST NOT encode that field as plain text.
- Final reasoning: Skipped debate and arbitration because all four phase-1 agents produced the same verdict.

## 29_32

- Gold class: `conflict`
- Predicted verdict: `incompatible`
- Confidence: `0.995`
- R29: OpenAPI documents that provide an Info Object termsOfService field MUST encode that field as plain text.
- R32: OpenAPI documents that provide an Info Object termsOfService field MUST encode that field as a Markdown string.
- Final reasoning: Skipped debate and arbitration because all four phase-1 agents produced the same verdict.

## 33_55

- Gold class: `conflict`
- Predicted verdict: `incompatible`
- Confidence: `1.0`
- R33: Each field name in the Paths Object MUST begin with a backslash (\).
- R55: Each field name in the Paths Object MUST begin with an alphanumeric character.
- Final reasoning: Skipped debate and arbitration because all four phase-1 agents produced the same verdict.

## 43_55

- Gold class: `conflict`
- Predicted verdict: `incompatible`
- Confidence: `1.0`
- R43: Each field name in the Paths Object MUST begin with a backslash (\).
- R55: Each field name in the Paths Object MUST begin with an alphanumeric character.
- Final reasoning: Skipped debate and arbitration because all four phase-1 agents produced the same verdict.
