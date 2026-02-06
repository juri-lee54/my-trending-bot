import os
import datetime
import requests
from bs4 import BeautifulSoup

URL = "https://github.com/trending/python?since=daily"

def get_trending_repos():
    # ... (이전과 동일한 크롤링 로직) ...
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(URL, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Failed to load page {URL}")

    soup = BeautifulSoup(response.text, 'html.parser')
    repos = []

    for row in soup.select('article.Box-row'):
        h2_tag = row.select_one('h2 a')
        repo_name = h2_tag.text.strip().replace('\n', '').replace(' ', '')
        repo_url = f"https://github.com/{repo_name}"

        p_tag = row.select_one('p')
        description = p_tag.text.strip() if p_tag else "설명 없음"

        stats_div = row.select_one('div.f6.color-fg-muted.mt-2')
        total_stars = stats_div.select_one('a').text.strip().replace(',', '')
        stars_today_tag = stats_div.select_one('span.d-inline-block.float-sm-right')
        stars_today = stars_today_tag.text.strip() if stars_today_tag else "0 stars today"

        repos.append({
            "name": repo_name,
            "url": repo_url,
            "description": description,
            "total_stars": total_stars,
            "stars_today": stars_today
        })
    return repos

def make_markdown_content(repos, date):
    """마크다운 내용을 생성하는 헬퍼 함수"""
    content = f"### 🔥 Today's Trends ({date})\n\n"
    content += f"Total: {len(repos)} repositories\n\n"
    content += "---\n\n"

    for idx, repo in enumerate(repos, 1):
        content += f"#### {idx}. [{repo['name']}]({repo['url']})\n"
        content += f"- **트렌딩 이유:** 🔥 {repo['stars_today']}\n"
        content += f"- **총 스타 수:** ⭐ {repo['total_stars']}\n"
        content += f"- **요약:** {repo['description']}\n\n"
    
    return content

def save_to_archive(repos):
    """archives 폴더에 날짜별 파일 저장"""
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    filename = f"archives/{today}.md"

    if not os.path.exists("archives"):
        os.makedirs("archives")

    content = f"# 🐍 GitHub Python Trending ({today})\n\n"
    content += make_markdown_content(repos, today)

    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"✅ Saved to archive: {filename}")

def update_readme(repos):
    """메인 README.md 업데이트"""
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    
    # README 헤더 부분
    readme_text = "# 🐍 GitHub Python Trending Bot\n\n"
    readme_text += "매일 자정에 자동으로 업데이트되는 Python 트렌딩 리포지토리 목록입니다.\n\n"
    readme_text += "데이터 출처: [GitHub Trending](https://github.com/trending/python?since=daily)\n\n"
    
    # 아카이브 링크
    readme_text += "## 📂 [과거 기록 보기 (Archives)](./archives)\n\n"
    readme_text += "---\n\n"
    
    # 오늘의 콘텐츠 추가
    readme_text += make_markdown_content(repos, today)

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme_text)
    print("✅ Updated README.md")

if __name__ == "__main__":
    try:
        data = get_trending_repos()
        save_to_archive(data)  # 1. 아카이브 저장
        update_readme(data)    # 2. 메인 리드미 업데이트
    except Exception as e:
        print(f"❌ Error: {e}")