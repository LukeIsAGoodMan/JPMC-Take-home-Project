import json
import random
from collections import defaultdict
from pathlib import Path

INPUT_FILE = Path("census_bureau.jsonl")

# 输出文件
HEAD_OUT = Path("sample_head.jsonl")
RANDOM_OUT = Path("sample_random.jsonl")
STRATIFIED_OUT = Path("sample_stratified.jsonl")

# 参数
HEAD_N = 100
RANDOM_N = 200
STRATIFIED_N_PER_LABEL = 100   # 每个 label 抽多少条
RANDOM_SEED = 42


def sample_head(input_file: Path, output_file: Path, n: int):
    """取前 n 行"""
    count = 0
    with input_file.open("r", encoding="utf-8") as fin, output_file.open("w", encoding="utf-8") as fout:
        for line in fin:
            if not line.strip():
                continue
            fout.write(line)
            count += 1
            if count >= n:
                break
    print(f"[head] wrote {count} rows -> {output_file}")


def sample_random_reservoir(input_file: Path, output_file: Path, n: int, seed: int = 42):
    """
    随机抽样 n 行，不需要把整个文件读进内存
    用 reservoir sampling，适合大文件
    """
    random.seed(seed)
    reservoir = []

    with input_file.open("r", encoding="utf-8") as fin:
        for i, line in enumerate(fin):
            if not line.strip():
                continue

            if len(reservoir) < n:
                reservoir.append(line)
            else:
                j = random.randint(0, i)
                if j < n:
                    reservoir[j] = line

    with output_file.open("w", encoding="utf-8") as fout:
        for line in reservoir:
            fout.write(line)

    print(f"[random] wrote {len(reservoir)} rows -> {output_file}")


def sample_stratified_by_label(input_file: Path, output_file: Path, n_per_label: int, seed: int = 42):
    """
    按 label 分层抽样
    假设每行是 JSON object，且有 'label' 字段
    """
    random.seed(seed)
    buckets = defaultdict(list)

    with input_file.open("r", encoding="utf-8") as fin:
        for line_num, line in enumerate(fin, start=1):
            line = line.strip()
            if not line:
                continue

            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                print(f"Skipping bad JSON at line {line_num}")
                continue

            label = obj.get("label", "__MISSING_LABEL__")
            buckets[label].append(line)

    total_written = 0
    with output_file.open("w", encoding="utf-8") as fout:
        for label, rows in buckets.items():
            k = min(n_per_label, len(rows))
            chosen = random.sample(rows, k)
            for row in chosen:
                fout.write(row + "\n")
            total_written += k
            print(f"[stratified] label={label!r}, available={len(rows)}, sampled={k}")

    print(f"[stratified] total wrote {total_written} rows -> {output_file}")


if __name__ == "__main__":
    sample_head(INPUT_FILE, HEAD_OUT, HEAD_N)
    sample_random_reservoir(INPUT_FILE, RANDOM_OUT, RANDOM_N, RANDOM_SEED)
    sample_stratified_by_label(INPUT_FILE, STRATIFIED_OUT, STRATIFIED_N_PER_LABEL, RANDOM_SEED)