# Datasets

## Included Files

| Dataset | Requirements | Conflict labels | Requirements |
| --- | --- | --- | ---: |
| ETCS-GOLD | `requirements/ETCS-GOLD.csv` | `labels/ETCS-GOLD.csv` | 64 |
| OpenAPI Specification 3.0 | `requirements/OpenAPI-Specification-3.0.csv` | `labels/OpenAPI-Specification-3.0.csv` | 58 |
| promise-project2 | `requirements/promise-project2.csv` | `labels/promise-project2.csv` | 64 |
| Broker-All | `requirements/Broker-All.csv` | `labels/Broker-All.csv` | 45 |
| Library-Gold | `requirements/Library-Gold.csv` | `labels/Library-Gold.csv` | 109 |

Requirement files contain an identifier and requirement text. Label files contain `R1`, `R2`, optional requirement-text copies, and a `class` field.

## Label Policy

- `class=duplicate` denotes redundancy and is not a conflict-positive label.
- Non-empty conflict-type classes in promise-project2 are conflict-positive.
- Blank classes in Library-Gold are conflict-positive because every listed row is a gold conflict pair in that source file.
- Pair identifiers are normalized as unordered pairs using ascending requirement IDs.

## Provenance and Licensing

The files are research datasets collected in the source workspace under their established dataset names. The workspace does not contain complete machine-readable upstream license metadata or authoritative source URLs for every dataset.

These files are included to reproduce the reported experiments, but they are not relicensed under the repository's MIT License. Users must verify and comply with each dataset's original terms before redistribution or commercial use.

SHA-256 values and exact source-workspace provenance are recorded in `release_manifest.json`.
