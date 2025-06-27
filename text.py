import json
import re

input_file = "docs.txt"
output_file = "docs_for_training.jsonl"

with open(input_file, "r", encoding="utf-8") as f:
    content = f.read()

# 문서 구분 패턴 (==== URL ====)
pattern = r"==== (https?://[^\s]+) ====\n"

# 분리된 문서 리스트 (URL 포함)
parts = re.split(pattern, content)

# re.split는 구분자 포함해서 분리: [본문1, URL1, 본문2, URL2, ...]
# 그래서 URL은 홀수 인덱스, 본문은 짝수 인덱스 위치에 있음
with open(output_file, "w", encoding="utf-8") as out_f:
    for i in range(1, len(parts), 2):
        url = parts[i].strip()
        text = parts[i+1].strip().replace("\n", " ")  # 줄바꿈을 공백으로 변환해도 되고 그대로 놔둬도 됨
        obj = {
            "url": url,
            "text": text
        }
        out_f.write(json.dumps(obj, ensure_ascii=False) + "\n")

print(f"완료! {output_file}에 저장되었습니다.")
