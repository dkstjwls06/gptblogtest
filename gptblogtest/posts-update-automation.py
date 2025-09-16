# import feedparser
# import os
# import re
# from markdownify import markdownify
# import html

# BLOG_URI = "https://indp.tistory.com/"
# GITHUB_URI = "https://github.com/dkstjwls06/gptblogtest/tree/main"


# def update(feeds: list):
#     for feed in feeds:
#         category = feed["tags"][0]["term"]
#         title = feed["title"]
#         content = create_content(title, feed["summary"])

#         file_name = get_file_name(category, title)
#         with open(file_name, "w", encoding="utf-8") as f:
#             f.write(content)
#         update_readme(category)


# def create_content(title: str, summary: str) -> str:
#     summary = html.unescape(summary)
#     contents = summary.split("<pre>")

#     for i in range(len(contents)):
#         code_block = re.search(r'<code\s+class="([^"]+)"', contents[i])
#         if code_block:
#             language = code_block.group(1)
#             if "language-" in language:
#                 language = language.replace("language-", "")
#             contents[i] = attach_language(language, "<pre>" + contents[i])
#         else:
#             contents[i] = markdownify(contents[i])
#     return f"{title}\n=\n" + "".join(contents)


# def attach_language(language: str, content: str) -> str:
#     content = markdownify(content).split("```")
#     return "\n```" + language + content[1] + "```\n" + "".join(content[2:])


# def get_file_name(category: str, title: str) -> str:
#     file_path = f"{category}/{title}/".replace(" ", "_")
#     os.makedirs(file_path, exist_ok=True)
#     return file_path + "README.md"


# def update_readme(category: str):
#     with open("README.md", "r", encoding="utf-8") as f:
#         readme = f.read()

#     if readme.find(category) == -1:
#         with open("README.md", "a", encoding="utf-8") as f:
#             f.write(f"\n- [{category}]({GITHUB_URI + category})")

#     sort_toc()


# def sort_toc():
#     with open("README.md", "r", encoding="utf-8") as f:
#         readme = f.read()

#     start = readme.find("## 목차")
#     toc = readme[start:].strip()
#     toc_lines = sorted(toc.split("\n")[1:])
#     sort_toc = "\n".join(["## 목차"] + toc_lines)

#     with open("README.md", "w", encoding="utf-8") as f:
#         f.write(readme.replace(toc, sort_toc))


# if __name__ == "__main__":
#     feeds = feedparser.parse(BLOG_URI + "rss")
#     update(feeds["entries"])

# gptblogtest/posts-update-automation.py (주요 부분만)
import feedparser, os, re, html, requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from markdownify import markdownify

BLOG_URI = "https://indp.tistory.com/"
GITHUB_URI = "https://github.com/dkstjwls06/gptblogtest/tree/main"

HEADERS = {"User-Agent": "Mozilla/5.0"}  # 403 방지용

def get_full_html(entry):
    # 1) content:encoded (feedparser는 entry.content[0].value)
    if entry.get('content'):
        return entry.content[0].value

    # 2) summary의 타입이 text/html이면 그대로 쓰기
    sd = entry.get('summary_detail', {})
    if sd.get('type') == 'text/html' and entry.get('summary'):
        return html.unescape(entry.summary)

    # 3) 최후: 실제 글 페이지를 긁어오기
    try:
        resp = requests.get(entry.link, headers=HEADERS, timeout=20)
        resp.raise_for_status()
        return extract_article_html(resp.text, entry.link)
    except Exception:
        return html.unescape(entry.get('summary', ''))

def extract_article_html(page_html, base_url):
    soup = BeautifulSoup(page_html, 'html.parser')
    # 티스토리에서 자주 쓰는 컨테이너 후보들
    for sel in ['.contents_style', '.article_view', 'article', '#content', '#mArticle', '.content']:
        node = soup.select_one(sel)
        if node:
            # lazy-loading 이미지 src 보정
            for img in node.find_all('img'):
                src = img.get('data-src') or img.get('data-original') or img.get('data-asset-url') or img.get('src')
                if src:
                    img['src'] = urljoin(base_url, src)
            return str(node)
    # 못 찾으면 통째로
    return str(soup.body or soup)

def create_content(title: str, html_text: str) -> str:
    # 코드블럭은 나중에 개선하고, 우선 전체를 markdownify
    md = markdownify(html_text)
    return f"{title}\n=\n{md}"

def safe(val: str) -> str:
    # 파일/폴더명 안전화
    val = re.sub(r'[\\/:*?"<>|]+', ' ', val).strip()
    return re.sub(r'\s+', '_', val)

def get_file_name(category: str, title: str) -> str:
    file_path = f"{safe(category)}/{safe(title)}/"
    os.makedirs(file_path, exist_ok=True)
    return file_path + "README.md"

def update_readme(category: str):
    if not os.path.exists("README.md"):
        with open("README.md", "w", encoding="utf-8") as f:
            f.write("# IndiePendentMusic Post Crawler\n\n## 목차\n")
    with open("README.md", "r", encoding="utf-8") as f:
        readme = f.read()
    if category not in readme:
        with open("README.md", "a", encoding="utf-8") as f:
            f.write(f"\n- [{category}]({GITHUB_URI}/{safe(category)})")  # 슬래시 누락 수정

    sort_toc()

def update(entries: list):
    for e in entries:
        category = (e.get("tags") or [{"term":"Uncategorized"}])[0]["term"]
        title = e["title"]
        html_text = get_full_html(e)
        content = create_content(title, html_text)
        with open(get_file_name(category, title), "w", encoding="utf-8") as f:
            f.write(content)
        update_readme(category)

if __name__ == "__main__":
    feeds = feedparser.parse(BLOG_URI + "rss")
    update(feeds["entries"])

