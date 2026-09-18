# Reproduction

## Environment

- Python 3.11 or newer.
- Provider credentials for DeepSeek, Kimi, Qwen, and an OpenAI-compatible arbiter.
- A local `all-MiniLM-L6-v2` sentence-transformer model or another compatible model path.

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -e ".[test]"
Copy-Item .env.example .env
```

Fill `.env` with your own credentials and endpoints. Do not commit `.env`.

## Preprocess

```powershell
python -m conflict_detection.cli.preprocess_cli `
  datasets\requirements\ETCS-GOLD.csv `
  --output-dir work\preprocessed `
  --threshold 0.24
```

## Detect

```powershell
python scripts\run_experiment.py `
  --input work\preprocessed\ETCS-GOLD_candidates.jsonl `
  --output-dir work\runs `
  --run-id etcs-public-run `
  --profile default
```

## Finalize

```powershell
python scripts\rebuild_results.py `
  --run-dir work\runs\etcs-public-run `
  --dataset-name ETCS-GOLD
```

## Reproduce Published Metrics Offline

```powershell
python scripts\evaluate_results.py
```

This evaluation command makes no API calls. A complete detection rerun does call multiple commercial model providers and may incur substantial cost.

The evaluation command also regenerates the uncertainty and abstention reports. To regenerate only those reports:

```powershell
python scripts/generate_uncertainty_reports.py
```

Final uncertainty is measured over all final verdict rows. Phase-1 view abstention rates are measured over canonical candidates with stored Phase-1 votes; canonical aliases are inherited results and are not counted as new view decisions. The report preserves the stored `needs_human_review` flag for provenance but recommends every final `uncertain` verdict for human review. Alias rows are collapsed to their source pair when review workload is counted.

Provider Batch jobs can take longer than synchronous calls to become available. Re-running the scheduler resumes from persisted successful records rather than deleting a run.
