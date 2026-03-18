import json
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def load_cleaned_articles(json_path="cleaned_articles.json"):
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            articles = json.load(f)
        print(f"Loaded {len(articles)} cleaned articles")
        return articles
    except FileNotFoundError:
        print(f"Error: {json_path} not found. Run preprocess.py first.")
        return []
    
def get_recommendations(user_interests: str, articles, top_n=5):
    if not articles:
        return []

    # Prepare documents: use clean_content from articles
    documents = [article["clean_content"] for article in articles if article["clean_content"].strip()]

    if not documents:
        print("No cleaned content found in articles.")
        return []

    # Create TF-IDF vectorizer
    vectorizer = TfidfVectorizer(
        max_features=5000,          # limit vocabulary size for speed
        min_df=1,                   # ignore terms that appear in <1 doc
        stop_words=None             # already removed in cleaning
    )

    #transform article
    tfidf_matrix = vectorizer.fit_transform(documents)

    #transform user_intresnts
    user_vector = vectorizer.transform([user_interests.lower()])

    #cosine similarity
    similarities = cosine_similarity(user_vector, tfidf_matrix).flatten()


    top_indices = similarities.argsort()[-top_n:][::-1]


    recommendations = []
    for idx in top_indices:
        score = similarities[idx]
        if score > 0:
            article = articles[idx]
            recommendations.append({
                "title": article["title"],
                "source": article["source"],
                "url": article["url"],
                "similarity_score": round(float(score), 4),
                "clean_content_preview": article["clean_content"][:150] + "..."
            })

    return recommendations

articles = load_cleaned_articles()

if __name__ == "__main__":

    if articles:
        print("Enter keyword: ")
        user_input = input().strip()

        if user_input:
            recs = get_recommendations(user_input, articles, top_n=5)

            if recs:
                print(f"\nTop {len(recs)} recommendations for: '{user_input}'\n")
                for i, rec in enumerate(recs, 1):
                    print(f"{i}. {rec['title']}")
                    print(f"   Source: {rec['source']}")
                    print(f"   Similarity: {rec['similarity_score']}")
                    print(f"   Preview: {rec['clean_content_preview']}")
                    print(f"   Link: {rec['url']}\n")
            else:
                print("No matching articles found (try different keywords)")
        else:
            print("No input given.")