import os
import datetime
import requests
from bs4 import BeautifulSoup
from openai import OpenAI

# OpenAI 클라이언트 설정 (GitHub Secrets에 OPENAI_API_KEY가 있어야 함)
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

URL = "https://github.com/trending/python?since=daily"

def get_korean_summary(repo_name, original_desc):
    """
    LLM을 사용하여 원문 설명을 한국어로 번역 및 요약합니다.
    """
    # API 키가 없으면 그냥 원문 반환 (에러 방지)
    if not client.api_key:
        return f"(API 키 없음) {original_desc}"

    prompt = f"""
    GitHub 리포지토리 이름: {repo_name}
    원문 설명: {original_desc}

    위 리포지토리가 무엇인지 **한국어**로 명확하게 번역 및 요약해줘.
    - 개발자가 이해하기 쉬운 전문적인 어조를 사용해.
    - '해요체'를 사용해 (예: ~하는 도구입니다).
    - 1~2문장으로 짧게 줄여.
    """

    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini", # 가성비 모델
            messages=[
                {"role": "system", "content": "You are a helpful technical translator."},
                {"role": "user", "content": prompt}
            ]
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        print(f"⚠️ AI Summary Error: {e}")
        return original_desc # 에러나면 원문 그대로 사용

def get_trending_repos():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(URL, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Failed to load page {URL}")

    soup = BeautifulSoup(response.text, 'html.parser')
    repos = []
    
    # ⚠️ 테스트를 위해 상위 5개만 처리 (전체 하려면 [:5] 제거)
    items = soup.select('article.Box-row')[:5]

    print(f"🔍 Found repositories. Starting AI translation...")

    for row in items:
        h2_tag = row.select_one('h2 a')
        repo_name = h2_tag.text.strip().replace('\n', '').replace(' ', '')
        repo_url = f"https://github.com/{repo_name}"

        # 원문 설명 가져오기
        p_tag = row.select_one('p')
        raw_description = p_tag.text.strip() if p_tag else "No description"

        # 통계 정보
        stats_div = row.select_one('div.f6.color-fg-muted.mt-2')
        total_stars = stats_div.select_one('a').text.strip().replace(',', '')
        stars_today_tag = stats_div.select_one('span.d-inline-block.float-sm-right')
        stars_today = stars_today_tag.text.strip() if stars_today_tag else "0 stars today"

        # 🔥 여기서 AI에게 한국어 번역을 요청!
        korean_summary = get_korean_summary(repo_name, raw_description)
        print(f"✅ Translated: {repo_name} -> {korean_summary}")

        repos.append({
            "name": repo_name,
            "url": repo_url,
            "stars_today": stars_today,
            "total_stars": total_stars,
            "summary": korean_summary  # 한국어 요약 저장
        })

    return repos

def make_markdown_content(repos, date):
    content = f"### 🔥 Today's Trends ({date})\n\n"
    content += f"Total: {len(repos)} repositories\n\n"
    content += "---\n\n"

    for idx, repo in enumerate(repos, 1):
        content += f"#### {idx}. [{repo['name']}]({repo['url']})\n"
        content += f"- **트렌딩 이유:** 🔥 {repo['stars_today']}\n"
        content += f"- **총 스타 수:** ⭐ {repo['total_stars']}\n"
        # 이제 여기가 한국어로 나옵니다!
        content += f"- **요약:** {repo['summary']}\n\n" 
    
    return content

def save_to_archive(repos):
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    filename = f"archives/{today}.md"
    if not os.path.exists("archives"):
        os.makedirs("archives")
    
    content = f"# 🐍 GitHub Python Trending ({today})\n\n" + make_markdown_content(repos, today)
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)

def update_readme(repos):
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    readme_text = "# 🐍 GitHub Python Trending Bot\n\n"
    readme_text += "매일 자정에 업데이트되는 Python 트렌딩 (AI 한국어 요약)\n\n"
    readme_text += "## 📂 [과거 기록 (Archives)](./archives)\n\n---\n\n"
    readme_text += make_markdown_content(repos, today)
    
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme_text)

if __name__ == "__main__":
    try:
        data = get_trending_repos()
        save_to_archive(data)
        update_readme(data)
    except Exception as e:
        print(f"❌ Error: {e}")