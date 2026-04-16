import json
from pathlib import Path

columns_path = Path("columns.txt")
schema_out = Path("schema.json")

with columns_path.open("r", encoding="utf-8") as f:
    columns = [line.strip() for line in f if line.strip()]

schema = {
    "dataset_name": "census_bureau",
    "n_columns": len(columns),
    "target_column": "label",
    "columns": [{"name": c, "type": "raw_string"} for c in columns],
    "notes": [
        "All fields preserved as raw strings for lossless conversion.",
        "Special values such as '?', 'Not in universe', '- 50000.', and '50000+.' are retained exactly as-is."
    ]
}

with schema_out.open("w", encoding="utf-8") as f:
    json.dump(schema, f, ensure_ascii=False, indent=2)

print(f"Saved schema to: {schema_out}")