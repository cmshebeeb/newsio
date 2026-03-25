import os
import requests
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv


load_dotenv()


API_KEY = os.getenv("NEWSAPI_API_KEY")

if not API_KEY:
    print("Error: NEWSAPI_API_KEY not found in .env file!")
    print("Please add your key in the .env file like this:")
    print("NEWSAPI_API_KEY=your_real_key_here")
    exit()


os.makedirs("data", exist_ok=True)

print("Fetching fresh news from NewsAPI...\n")

url = "https://newsapi.org/v2/everything"

yesterday = (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d")

params = {
    "q": "news",
    "language": "en",
    "from": yesterday,
    "sortBy": "publishedAt",
    "pageSize": 30,
    "apiKey": API_KEY
}

response = requests.get(url, params=params)

if response.status_code == 200:
    data = response.json()
    articles = data.get("articles", [])
    
    print(f"API Status: {data.get('status')}")
    print(f"Total Results Available: {data.get('totalResults')}")
    print(f"This page returned: {len(articles)} articles\n")

    clean_articles = []
    
    for article in articles:
        title = article.get('title', 'No title')
        desc = article.get('description') or ''
        source_name = article.get('source', {}).get('name', 'Unknown')
        url_link = article.get('url', 'No url')
        published = article.get('publishedAt', 'Unknown')

        full_content = f"{title}. {desc}".strip()

        clean_articles.append({
            "title": title,
            "description": desc,
            "content": full_content,
            "source": source_name,
            "url": url_link,
            "published_at": published,
            "fetched_at": datetime.now().isoformat()
        })
        
        print(f"{len(clean_articles)}. {title}")
        print(f"   {desc[:120]}{'...' if len(desc) > 120 else ''}")
        print(f"   Source: {source_name} | {published[:10]}\n")

    with open("data/articles.json", "w", encoding="utf-8") as f:
        json.dump(clean_articles, f, indent=2, ensure_ascii=False)
    
    print(f"Successfully saved {len(clean_articles)} articles to data/articles.json")

else:
    print(f"Error {response.status_code}: {response.text}")
    if response.status_code == 401:
        print("Please check if your NEWSAPI_API_KEY in .env is correct.")