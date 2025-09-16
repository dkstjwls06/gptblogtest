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
# ________________________________________________________________
# gptblogtest/posts-update-automation.py (주요 부분만)
# import feedparser, os, re, html, requests
# from bs4 import BeautifulSoup
# from urllib.parse import urljoin
# from markdownify import markdownify

# BLOG_URI = "https://indp.tistory.com/"
# GITHUB_URI = "https://github.com/dkstjwls06/gptblogtest/tree/main"

# HEADERS = {"User-Agent": "Mozilla/5.0"}  # 403 방지용

# def get_full_html(entry):
#     # 1) content:encoded (feedparser는 entry.content[0].value)
#     if entry.get('content'):
#         return entry.content[0].value

#     # 2) summary의 타입이 text/html이면 그대로 쓰기
#     sd = entry.get('summary_detail', {})
#     if sd.get('type') == 'text/html' and entry.get('summary'):
#         return html.unescape(entry.summary)

#     # 3) 최후: 실제 글 페이지를 긁어오기
#     try:
#         resp = requests.get(entry.link, headers=HEADERS, timeout=20)
#         resp.raise_for_status()
#         return extract_article_html(resp.text, entry.link)
#     except Exception:
#         return html.unescape(entry.get('summary', ''))

# def extract_article_html(page_html, base_url):
#     soup = BeautifulSoup(page_html, 'html.parser')
#     # 티스토리에서 자주 쓰는 컨테이너 후보들
#     for sel in ['.contents_style', '.article_view', 'article', '#content', '#mArticle', '.content']:
#         node = soup.select_one(sel)
#         if node:
#             # lazy-loading 이미지 src 보정
#             for img in node.find_all('img'):
#                 src = img.get('data-src') or img.get('data-original') or img.get('data-asset-url') or img.get('src')
#                 if src:
#                     img['src'] = urljoin(base_url, src)
#             return str(node)
#     # 못 찾으면 통째로
#     return str(soup.body or soup)

# def create_content(title: str, html_text: str) -> str:
#     # 코드블럭은 나중에 개선하고, 우선 전체를 markdownify
#     md = markdownify(html_text)
#     return f"{title}\n=\n{md}"

# def safe(val: str) -> str:
#     # 파일/폴더명 안전화
#     val = re.sub(r'[\\/:*?"<>|]+', ' ', val).strip()
#     return re.sub(r'\s+', '_', val)

# def get_file_name(category: str, title: str) -> str:
#     file_path = f"{safe(category)}/{safe(title)}/"
#     os.makedirs(file_path, exist_ok=True)
#     return file_path + "README.md"

# def update_readme(category: str):
#     if not os.path.exists("README.md"):
#         with open("README.md", "w", encoding="utf-8") as f:
#             f.write("# IndiePendentMusic Post Crawler\n\n## 목차\n")
#     with open("README.md", "r", encoding="utf-8") as f:
#         readme = f.read()
#     if category not in readme:
#         with open("README.md", "a", encoding="utf-8") as f:
#             f.write(f"\n- [{category}]({GITHUB_URI}/{safe(category)})")  # 슬래시 누락 수정


# def update(entries: list):
#     for e in entries:
#         category = (e.get("tags") or [{"term":"Uncategorized"}])[0]["term"]
#         title = e["title"]
#         html_text = get_full_html(e)
#         content = create_content(title, html_text)
#         with open(get_file_name(category, title), "w", encoding="utf-8") as f:
#             f.write(content)
#         update_readme(category)

# if __name__ == "__main__":
#     feeds = feedparser.parse(BLOG_URI + "rss")
#     update(feeds["entries"])
# _______________________________________________________
import feedparser
import os
import re
import html
import hashlib
from urllib.parse import urljoin, urlparse, unquote
from urllib.request import urlopen, Request

BLOG_URI = "https://indp.tistory.com/"
GITHUB_URI = "https://github.com/dkstjwls06/gptblogtest/tree/main"

# markdownify는 기존 워크플로에서 설치됨
from markdownify import markdownify


# -----------------------------
# 유틸
# -----------------------------
def safe(val: str) -> str:
    """파일/폴더명 안전화"""
    val = re.sub(r'[\\/:*?"<>|]+', " ", val).strip()
    return re.sub(r"\s+", "_", val)


def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)
    return path


def http_get(url: str, timeout: int = 20, ua: str = "Mozilla/5.0") -> str:
    """간단한 GET (표준 라이브러리)"""
    req = Request(url, headers={"User-Agent": ua})
    with urlopen(req, timeout=timeout) as resp:
        # 인코딩 헤더가 없을 수 있으니 utf-8 기준, 실패는 무시
        data = resp.read()
        try:
            charset = resp.headers.get_content_charset() or "utf-8"
        except Exception:
            charset = "utf-8"
        return data.decode(charset, errors="ignore")


def guess_ext_from_url(u: str) -> str:
    """URL에서 확장자 추론 (없으면 .jpg)"""
    path = urlparse(u).path
    filename = os.path.basename(path)
    if "." in filename:
        ext = filename.split(".")[-1].lower()
        # 너무 긴 쿼리 꼬임 방지
        ext = re.sub(r"[^a-z0-9]", "", ext)[:5]
        if ext:
            return "." + ext
    return ".jpg"


# -----------------------------
# 이미지 처리
# -----------------------------
_IMG_TAG_RE = re.compile(r"<img\b[^>]*>", re.IGNORECASE | re.DOTALL)
_ATTR_RE_TPL = r'{name}\s*=\s*["\']([^"\']+)["\']'

def _get_attr(tag_html: str, name: str):
    m = re.search(_ATTR_RE_TPL.format(name=name), tag_html, flags=re.IGNORECASE)
    return m.group(1) if m else None


def _set_or_insert_src(tag_html: str, new_src: str) -> str:
    """img 태그의 src를 new_src로 교체(없으면 삽입)"""
    if re.search(r"\ssrc\s*=", tag_html, flags=re.IGNORECASE):
        return re.sub(r'\ssrc\s*=\s*["\'][^"\']*["\']',
                      f' src="{new_src}"',
                      tag_html, count=1, flags=re.IGNORECASE)
    # self-closing 처리
    if tag_html.endswith("/>"):
        return tag_html[:-2] + f' src="{new_src}" />'
    return tag_html[:-1] + f' src="{new_src}">'


def download_and_localize_images(html_text: str, base_url: str, asset_dir: str) -> str:
    """
    HTML 내 이미지들을 로컬 ./images/로 저장하고,
    img 태그의 src를 로컬 상대 경로로 치환하여 HTML을 반환.
    """
    images_dir = ensure_dir(os.path.join(asset_dir, "images"))
    url_to_local = {}

    def _download(url: str) -> str:
        if url in url_to_local:
            return url_to_local[url]
        # 파일명: URL md5 + 확장자
        h = hashlib.md5(url.encode("utf-8")).hexdigest()  # nosec - 콘텐츠 캐시용
        ext = guess_ext_from_url(url)
        local_name = f"{h}{ext}"
        local_abs = os.path.join(images_dir, local_name)
        if not os.path.exists(local_abs):  # 캐시
            try:
                req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
                with urlopen(req, timeout=30) as resp, open(local_abs, "wb") as f:
                    f.write(resp.read())
            except Exception:
                # 다운로드 실패 시 원본 URL 유지하되, 이후 교체에서 스킵하도록 기록
                url_to_local[url] = None
                return None
        rel = "./images/" + local_name
        url_to_local[url] = rel
        return rel

    new_html = html_text
    for m in _IMG_TAG_RE.finditer(html_text):
        tag = m.group(0)

        # data-* 우선(src 대체)
        cand = (_get_attr(tag, "data-src") or
                _get_attr(tag, "data-original") or
                _get_attr(tag, "data-asset-url") or
                _get_attr(tag, "src"))
        if not cand:
            continue

        abs_url = urljoin(base_url, cand)
        local_rel = _download(abs_url)
        if not local_rel:
            continue

        new_tag = _set_or_insert_src(tag, local_rel)
        # 원본 태그 한 번만 치환
        new_html = new_html.replace(tag, new_tag, 1)

    return new_html


# -----------------------------
# 본문 추출(피드 → HTML)
# -----------------------------
def get_full_html(entry) -> tuple[str, str]:
    """
    entry에서 가능한 '가장 풍부한' HTML을 반환.
    (html_text, base_url)
    base_url은 이미지 절대경로 변환 및 다운로드에 활용.
    """
    # 1) content:encoded
    if entry.get("content"):
        return entry.content[0].value, entry.get("link", BLOG_URI)

    # 2) summary_detail이 html일 때
    sd = entry.get("summary_detail", {})
    if sd.get("type") == "text/html" and entry.get("summary"):
        return html.unescape(entry.summary), entry.get("link", BLOG_URI)

    # 3) 최후수단: 실제 페이지 HTML 전체
    link = entry.get("link") or BLOG_URI
    try:
        page = http_get(link)
        return page, link
    except Exception:
        # 4) 완전 실패 시 summary 텍스트라도
        return html.unescape(entry.get("summary", "")), link


# -----------------------------
# 파일 경로/README
# -----------------------------
def get_post_dir(category: str, title: str) -> str:
    file_path = f"{safe(category)}/{safe(title)}/"
    ensure_dir(file_path)
    return file_path


def get_readme_path(post_dir: str) -> str:
    return os.path.join(post_dir, "README.md")


def update_readme(category: str):
    """
    간단한 목차만 유지. sort_toc()는 더 이상 호출하지 않음(요구사항).
    """
    if not os.path.exists("README.md"):
        with open("README.md", "w", encoding="utf-8") as f:
            f.write("# IndiePendentMusic Post Crawler\n\n## 목차\n")

    with open("README.md", "r", encoding="utf-8") as f:
        readme = f.read()

    # 카테고리 항목이 없으면 추가
    cat = safe(category)
    link = f"{GITHUB_URI}/{cat}"
    if cat not in readme:
        with open("README.md", "a", encoding="utf-8") as f:
            f.write(f"\n- [{cat}]({link})")


# -----------------------------
# 마크다운 변환
# -----------------------------
def create_content(title: str, html_text: str) -> str:
    """
    HTML → Markdown 변환.
    img src는 이미 로컬 경로로 치환되었다고 가정.
    """
    md = markdownify(html_text)
    return f"{title}\n=\n{md}"


# -----------------------------
# 메인 로직
# -----------------------------
def update(feeds: list):
    for e in feeds:
        category = (e.get("tags") or [{"term": "Uncategorized"}])[0]["term"]
        title = e["title"]

        # 글 폴더
        post_dir = get_post_dir(category, title)

        # HTML 확보
        raw_html, base_url = get_full_html(e)

        # 이미지 다운로드 & 로컬 경로로 치환
        html_with_local_imgs = download_and_localize_images(raw_html, base_url, post_dir)

        # Markdown 생성
        content = create_content(title, html_with_local_imgs)

        # 쓰기
        with open(get_readme_path(post_dir), "w", encoding="utf-8") as f:
            f.write(content)

        # README(루트) 갱신
        update_readme(category)


if __name__ == "__main__":
    feeds = feedparser.parse(BLOG_URI + "rss")
    update(feeds["entries"])
