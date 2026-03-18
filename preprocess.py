import string
import json
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

def clean_text(text: str) -> str:
    """
    Clean a single piece of text:
    - lowercase
    - remove punctuation
    - remove extra spaces
    - remove stopwords
    """
    if not text:
        return ""
    
    text = text.lower()
    
    text = text.translate(str.maketrans('', '', string.punctuation))
    

    text = ''.join([char for char in text if not char.isdigit()])
    

    text = ' '.join(text.split())
    

    words = text.split()
    cleaned_words = [word for word in words if word not in ENGLISH_STOP_WORDS]
    
    return ' '.join(cleaned_words)


def load_and_clean_articles(json_path="articles.json"):

    #Load articles from JSON and add a 'clean_content' field
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            articles = json.load(f)
    except FileNotFoundError:
        print(f"Error: {json_path} not found!")
        return []
    
    print(f"Loaded {len(articles)} articles from {json_path}")
    
    for article in articles:
        raw_content = article.get("content", "")
        cleaned = clean_text(raw_content)
        article["clean_content"] = cleaned

    return articles


if __name__ == "__main__":
    # Test run
    cleaned_articles = load_and_clean_articles()
    if cleaned_articles:
        print(f"\nSuccessfully cleaned {len(cleaned_articles)} articles.")

        with open("cleaned_articles.json", "w", encoding="utf-8") as f:
            json.dump(cleaned_articles, f, indent=2, ensure_ascii=False)
        print("Saved cleaned version to cleaned_articles.json")