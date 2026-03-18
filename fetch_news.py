import requests


API_KEY = "2fe51de664a64956ac332834ea7fa5ea"


url = "https://newsapi.org/v2/top-headlines"
params = {
    "country": "us",           
    "category": "general",  
    "apiKey": API_KEY,
    "pageSize": 10              
}

response = requests.get(url, params=params)

if response.status_code == 200:
    data = response.json()
    articles = data.get("articles", [])
    
    print(f"Found {len(articles)} articles!\n")
    
    for i, article in enumerate(articles, 1):
        title = article.get('title', 'No title')
        desc = article.get('description') or ''          # ← safe: None → empty string
        source_name = article.get('source', {}).get('name', 'Unknown')
        url = article.get('url', 'No url')
        
        print(f"{i}. {title}")
        print(f"   {desc[:120]}{'...' if len(desc) > 120 else ''}")  # safe slice
        print(f"   Source: {source_name}")
        print(f"   URL: {url}\n")
else:
    print("Error:", response.status_code)
    print(response.text)