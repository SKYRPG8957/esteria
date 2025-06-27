import json
import os

# 예시 입력 파일 경로 (나중에 실제 경로로 바꿔야 함)
INPUT_FILE = "/mnt/data/docs_for_training.jsonl"
SUMMARY_FILE = "/mnt/data/docs_for_training_summary.md"

# 요약에 포함할 최대 명령어/엔티티 수
MAX_ITEMS_PER_SECTION = 20

# 결과 저장용
commands = []
entities = set()
nbt_keys = set()

# 줄 단위로 JSONL 파일 읽기
with open(INPUT_FILE, "r", encoding="utf-8") as f:
    for line in f:
        try:
            data = json.loads(line)
            if "command" in data:
                commands.append(data["command"])

            if "entities" in data:
                entities.update(data["entities"])

            if "nbt" in data:
                if isinstance(data["nbt"], dict):
                    nbt_keys.update(data["nbt"].keys())

        except json.JSONDecodeError:
            continue

# 요약 파일 작성
with open(SUMMARY_FILE, "w", encoding="utf-8") as f:
    f.write("# Minecraft Command Summary\n\n")

    f.write("## Commands\n")
    for cmd in commands[:MAX_ITEMS_PER_SECTION]:
        f.write(f"- `{cmd}`\n")
    f.write("\n")

    f.write("## Entities\n")
    for ent in list(entities)[:MAX_ITEMS_PER_SECTION]:
        f.write(f"- `{ent}`\n")
    f.write("\n")

    f.write("## NBT Keys\n")
    for key in list(nbt_keys)[:MAX_ITEMS_PER_SECTION]:
        f.write(f"- `{key}`\n")
    f.write("\n")

SUMMARY_FILE
