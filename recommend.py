import json
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import subprocess
import os


DATA_DIR = "data"
PROFILE_FILE = os.path.join(DATA_DIR, "user_profile.json")
CLEANED_ARTICLES_FILE = os.path.join(DATA_DIR, "cleaned_articles.json")

def load_cleaned_articles():
    try:
        with open(CLEANED_ARTICLES_FILE, "r", encoding="utf-8") as f:
            articles = json.load(f)
        print(f"Loaded {len(articles)} cleaned articles from {CLEANED_ARTICLES_FILE}")
        return articles
    except FileNotFoundError:
        print(f"Error: {CLEANED_ARTICLES_FILE} not found.")
        print("Please run: python fetch_news.py  and  python preprocess.py first")
        return []
    except Exception as e:
        print(f"Error loading articles: {e}")
        return []


def load_user_profile():
    try:
        with open(PROFILE_FILE, "r", encoding="utf-8") as f:
            profile = json.load(f)
        return profile
    except FileNotFoundError:
        return {"liked_articles": [], "disliked_articles": []}


def save_user_profile(profile):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(PROFILE_FILE, "w", encoding="utf-8") as f:
        json.dump(profile, f, indent=2, ensure_ascii=False)
    print("User profile saved.")


def get_recommendations(user_interests: str, articles, top_n=5):
    if not articles:
        return []

    documents = [a.get("clean_content", "") for a in articles if a.get("clean_content", "").strip()]
    if not documents:
        return []

    vectorizer = TfidfVectorizer(max_features=5000, min_df=1)
    tfidf_matrix = vectorizer.fit_transform(documents)

    user_vector = vectorizer.transform([user_interests.lower()])

    similarities = cosine_similarity(user_vector, tfidf_matrix).flatten()

    top_indices = similarities.argsort()[-top_n*2:][::-1]

    recommendations = []
    seen_urls = set()

    for idx in top_indices:
        if len(recommendations) >= top_n:
            break
        score = similarities[idx]
        if score <= 0.01:
            continue
        article = articles[idx]
        url = article.get("url")
        if url in seen_urls:
            continue
        seen_urls.add(url)
        recommendations.append({
            "title": article.get("title", "No title"),
            "source": article.get("source", "Unknown"),
            "url": url,
            "similarity_score": round(float(score), 4),
            "clean_content_preview": article.get("clean_content", "")[:150] + "..."
        })

    return recommendations


def show_recommendations(recs):
    if not recs:
        print("No recommendations found.")
        return

    print(f"\nTop {len(recs)} recommendations:\n")
    for i, rec in enumerate(recs, 1):
        print(f"{i}. {rec['title']}")
        print(f"   Source: {rec['source']}")
        print(f"   Similarity: {rec['similarity_score']}")
        print(f"   Preview: {rec['clean_content_preview']}")
        print(f"   Link: {rec['url']}\n")


def main():
    print("=== NewsIO - Personalized News Recommender with AI Summarization ===\n")

    while True:
        articles = load_cleaned_articles()
        if not articles:
            print("\nWould you like to fetch fresh news now? (y/n)")
            if input("> ").strip().lower() == 'y':
                subprocess.run(["python", "fetch_news.py"])
                subprocess.run(["python", "preprocess.py"])
                continue
            else:
                break

        profile = load_user_profile()
        liked_urls = set(profile.get("liked_articles", []))
        disliked_urls = set(profile.get("disliked_articles", []))

        print(f"Liked: {len(liked_urls)} | Disliked: {len(disliked_urls)}")

        print("\nOptions:")
        print("  1. Get personalized recommendations")
        print("  2. Fetch fresh news")
        print("  3. Show my liked articles")
        print("  4. Quit")

        choice = input("\nChoose (1-4): ").strip()

        if choice == "4":
            print("Goodbye!")
            break

        elif choice == "2":
            print("Fetching fresh news...")
            subprocess.run(["python", "fetch_news.py"])
            subprocess.run(["python", "preprocess.py"])
            continue

        elif choice == "3":
            if liked_urls:
                print("\nYour liked articles:")
                for url in liked_urls:
                    for art in articles:
                        if art.get("url") == url:
                            print(f"- {art['title'][:80]}...")
                            break
            else:
                print("No liked articles yet.")
            continue

        elif choice == "1":
            user_input = input("\nEnter your interests (or press Enter to use history): ").strip()

            filtered_articles = [a for a in articles if a.get("url") not in liked_urls and a.get("url") not in disliked_urls]

            if not filtered_articles:
                print("No new articles left. Fetch more news.")
                continue

            recs = get_recommendations(user_input or "general news", filtered_articles)

            show_recommendations(recs)

            # Feedback creation
            if recs:
                print("\nFeedback (l = like + get AI summary, d = dislike, s = skip):")
                for rec in recs:
                    choice_fb = input(f"\n{rec['title'][:65]}... → (l/d/s): ").strip().lower()
                    url = rec["url"]

                    if choice_fb == 'l':
                        if url not in profile["liked_articles"]:
                            profile["liked_articles"].append(url)
                            
                            # Generate AI Summary
                            print(" Generating AI summary...")
                            full_article = next((a for a in articles if a.get("url") == url), None)
                            if full_article:
                                article_text = full_article.get("content", full_article.get("title", "") + ". " + full_article.get("description", ""))
                                from summarizer.llm_summarizer import generate_summary
                                summary = generate_summary(article_text)
                                print("\nAI Summary:")
                                print(summary)
                                print("-" * 60)
                            print("  Added to profile.")
                    
                    elif choice_fb == 'd':
                        if url not in profile["disliked_articles"]:
                            profile["disliked_articles"].append(url)
                            print("Disliked.")
                    else:
                        print("Skipped...")

                save_user_profile(profile)

        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()