import csv
import json
from pathlib import Path

columns_path = Path("./columns.txt")
data_path = Path("./data.txt")

csv_out = Path("census_bureau_with_header.csv")
jsonl_out = Path("census_bureau.jsonl")

# 1) 读取列名
with columns_path.open("r", encoding="utf-8") as f:
    columns = [line.strip() for line in f if line.strip()]

print(f"Loaded {len(columns)} columns")

# 2) 转换
row_count = 0
bad_rows = 0

with data_path.open("r", encoding="utf-8", newline="") as fin, \
     csv_out.open("w", encoding="utf-8", newline="") as fcsv, \
     jsonl_out.open("w", encoding="utf-8") as fjsonl:

    reader = csv.reader(fin)
    writer = csv.writer(fcsv)

    # 写入带表头 CSV
    writer.writerow(columns)

    for i, row in enumerate(reader, start=1):
        if not row:
            continue

        if len(row) != len(columns):
            bad_rows += 1
            if bad_rows <= 10:
                print(f"Bad row {i}: got {len(row)} fields, expected {len(columns)}")
            continue

        # 保持无损：全部先按字符串保留
        row = [x.strip() for x in row]

        writer.writerow(row)

        record = dict(zip(columns, row))
        fjsonl.write(json.dumps(record, ensure_ascii=False) + "\n")

        row_count += 1
        if row_count % 100000 == 0:
            print(f"Processed {row_count} rows")

print(f"Done. Wrote {row_count} rows.")
print(f"Skipped {bad_rows} malformed rows.")
print(f"CSV saved to: {csv_out}")
print(f"JSONL saved to: {jsonl_out}")