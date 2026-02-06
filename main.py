import os
import datetime
import requests
from bs4 import BeautifulSoup

# GitHub 트렌딩 페이지 (Python 언어 필터링)
URL = "https://github.com/trending/python?since=daily"

def get_trending_repos():
    """
    GitHub Python 트렌딩 페이지를 크롤링하여 정보를 리스트로 반환합니다.
    """
    # 봇 차단 방지를 위한 헤더 설정
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    response = requests.get(URL, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Failed to load page {URL}")

    soup = BeautifulSoup(response.text, 'html.parser')
    repos = []

    # 각 리포지토리 행(Row) 가져오기
    for row in soup.select('article.Box-row'):
        # 1. 리포지토리 이름 및 링크
        h2_tag = row.select_one('h2 a')
        repo_name = h2_tag.text.strip().replace('\n', '').replace(' ', '')
        repo_url = f"https://github.com/{repo_name}"

        # 2. 설명 (요약)
        p_tag = row.select_one('p')
        description = p_tag.text.strip() if p_tag else "설명 없음 (No description provided)"

        # 3. 스타 수 정보 (전체 스타, 오늘의 스타)
        # 마지막 div에 통계 정보가 들어있음
        stats_div = row.select_one('div.f6.color-fg-muted.mt-2')
        
        # 전체 스타 수
        total_stars = stats_div.select_one('a').text.strip().replace(',', '')
        
        # 오늘의 스타 수 (트렌딩 이유)
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

def save_to_markdown(repos):
    """
    수집된 데이터를 날짜별 마크다운 파일로 저장합니다.
    """
    # 오늘 날짜 구하기 (YYYY-MM-DD)
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    filename = f"archives/{today}.md"

    # archives 폴더가 없으면 생성
    if not os.path.exists("archives"):
        os.makedirs("archives")

    # 마크다운 내용 작성
    markdown_text = f"# 🐍 GitHub Python Trending ({today})\n\n"
    markdown_text += f"Total: {len(repos)} repositories\n\n"
    markdown_text += "---\n\n"

    for idx, repo in enumerate(repos, 1):
        markdown_text += f"### {idx}. [{repo['name']}]({repo['url']})\n"
        markdown_text += f"- **트렌딩 이유:** 🔥 {repo['stars_today']}\n"
        markdown_text += f"- **총 스타 수:** ⭐ {repo['total_stars']}\n"
        markdown_text += f"- **요약:** {repo['description']}\n\n"
        markdown_text += "---\n"

    # 파일 쓰기
    with open(filename, "w", encoding="utf-8") as f:
        f.write(markdown_text)
    
    print(f"✅ Successfully saved to {filename}")

if __name__ == "__main__":
    try:
        data = get_trending_repos()
        save_to_markdown(data)
    except Exception as e:
        print(f"❌ Error: {e}")