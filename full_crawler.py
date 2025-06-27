import aiohttp
import asyncio
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import os
import json
import hashlib

BASE_URL = "https://learn.microsoft.com/en-us/minecraft/creator/documents/customcommands"
DOMAIN = "https://learn.microsoft.com"
DATA_DIR = "docs_data"  # 문서별 저장 디렉터리

os.makedirs(DATA_DIR, exist_ok=True)

# URL -> 저장 파일명 매핑 (간단히 해시 이용)
def url_to_filename(url):
    return hashlib.sha256(url.encode('utf-8')).hexdigest() + ".json"

# 저장된 문서 불러오기 (변경 감지용)
def load_saved_doc(url):
    fname = os.path.join(DATA_DIR, url_to_filename(url))
    if os.path.exists(fname):
        with open(fname, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

# 저장하기
def save_doc(url, data):
    fname = os.path.join(DATA_DIR, url_to_filename(url))
    with open(fname, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# 문서 파싱 & 필요한 데이터 추출
def parse_document(html, url):
    soup = BeautifulSoup(html, "html.parser")

    # 문서 본문 텍스트(예시로 main 태그)
    main_content = soup.select_one("main")
    paragraphs = []
    if main_content:
        paragraphs = [p.get_text(separator="\n").strip() for p in main_content.find_all(['p','li','h1','h2','h3','h4','h5','h6']) if p.get_text(strip=True)]

    # 코드 블록 추출
    code_blocks = []
    for code in main_content.find_all("pre"):
        code_blocks.append({
            "text": code.get_text()
        })

    # 문서 제목
    title = soup.title.string if soup.title else ""

    return {
        "url": url,
        "title": title,
        "paragraphs": paragraphs,
        "code_blocks": code_blocks
    }

# 크롤링 함수
async def crawl_url(session, url, visited):
    if url in visited:
        return []
    visited.add(url)

    try:
        async with session.get(url) as resp:
            if resp.status != 200:
                print(f"Failed to fetch {url}: {resp.status}")
                return []
            html = await resp.text()

            parsed = parse_document(html, url)

            # 변경 감지: 기존 데이터와 비교해서 변경됐으면 저장
            old_doc = load_saved_doc(url)
            if old_doc != parsed:
                save_doc(url, parsed)
                print(f"[UPDATED] {url}")
            else:
                print(f"[UNCHANGED] {url}")

            # 다음 링크 찾기
            soup = BeautifulSoup(html, "html.parser")
            links = []
            for a in soup.find_all("a", href=True):
                full_url = urljoin(url, a['href'])
                if full_url.startswith(DOMAIN) and "/minecraft/creator/documents/" in full_url and full_url not in visited:
                    links.append(full_url)

            return links

    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return []

# 메인 크롤러
async def main_crawler(start_url):
    visited = set()
    to_crawl = [start_url]

    async with aiohttp.ClientSession() as session:
        while to_crawl:
            tasks = [crawl_url(session, url, visited) for url in to_crawl]
            results = await asyncio.gather(*tasks)

            # 새로 발견한 URL들 합치기
            new_urls = set()
            for urls in results:
                new_urls.update(urls)

            to_crawl = list(new_urls - visited)

if __name__ == "__main__":
    asyncio.run(main_crawler(BASE_URL))
