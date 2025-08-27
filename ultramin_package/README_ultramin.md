# Ultra-minimal CATIA harvesting package

This package keeps **two separate, efficient tables** in a single SQLite DB:

1) `doc_functions_ultramin` ← **CAADoc scrape**
   - `function_key` (factory.method, lowercase)
   - `api_factory`, `api_method`
   - `action_label` (normalized: `AddNewPlaneOffset` → `create_plane_offset`)
   - `doc_url`
   - `tokens_json` (array of tokens for your function-matcher)

2) `harvested_steps_ultramin` ← **PDF harvest**
   - `step_id` (execution order)
   - `action_label` (e.g., `create_plane_offset`, `symmetry`, …)
   - `description` (short)
   - `params_json` (only parsed parameters/values)
   - `produces_json` (features created)
   - `references_json` (dependencies)
   - `code_lang`, `generated_code` (placeholders for your LLM)

## Install
```
pip install -r requirements.txt
```

## Run (either or both)
```
# Scrape CAADoc (prefer http)
python run_all_ultramin.py --db harvested_ultramin.db \
  --master "http://catiadoc.free.fr/online/interfaces/CAAMasterIdx.htm" \
  --overwrite-docs --log-level INFO

# Harvest your PDF
python run_all_ultramin.py --db harvested_ultramin.db \
  --pdf "Flying-Wing-Instructions.pdf" --log-level INFO

# Do both in one go
python run_all_ultramin.py --db harvested_ultramin.db \
  --master "http://catiadoc.free.fr/online/interfaces/CAAMasterIdx.htm" \
  --pdf "Flying-Wing-Instructions.pdf" \
  --overwrite-db --overwrite-docs --log-level DEBUG
```

## Notes
- **No coupling**: doc scrape and PDF harvest are stored in *separate* tables.
- **Minimal & LLM-friendly**: only the columns needed for robust generation.
- **Your matcher** can align `action_label` + `tokens_json` with `harvested_steps_ultramin.action_label`.
