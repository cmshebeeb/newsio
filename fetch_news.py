import requests
import json
from datetime import datetime, timedelta


API_KEY = "2fe51de664a64956ac332834ea7fa5ea"
yesterday = (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d")

url = "https://newsapi.org/v2/top-headlines"
params = {
    "from": yesterday,
    "language": "en",
    "sortBy": "publishedAt",
    "pageSize": 20,
    "apiKey": API_KEY
}

response = requests.get(url, params=params)

if response.status_code == 200:
    data = response.json()
    articles = data.get("articles", [])
    
    print(f"Found {len(articles)} articles!\n")

    clean_articles = []
    
    for article in articles:
        title = article.get('title', 'No title')
        desc = article.get('description') or ''
        source_name = article.get('source', {}).get('name', 'Unknown')
        url = article.get('url', 'No url')
        published = article.get('publishedAt', 'Unknown')

        full_content = f"{title}. {desc}".strip()

        clean_articles.append({
            "title": title,
            "description": desc,
            "content": full_content,
            "source": source_name,
            "url": url,
            "published_at": published,
            "fetched_at": datetime.now().isoformat()
        })
        
        print(f"{len(clean_articles)}. {title}")
        print(f"   {desc[:100]}{'...' if len(desc) > 100 else ''}")
        print(f"   Source: {source_name} | {published[:10]}\n")

    with open("articles.json", "w", encoding="utf-8") as f:
        json.dump(clean_articles, f, indent=2, ensure_ascii=False)
    
    print(f"\nSaved {len(clean_articles)} articles to articles.json")

else:
    print("Error:", response.status_code)
    print(response.text)