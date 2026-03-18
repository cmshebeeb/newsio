import json
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

PROFILE_FILE = "user_profile.json"
CLEANED_ARTICLES_FILE = "cleaned_articles.json"


def load_cleaned_articles():
    try:
        with open(CLEANED_ARTICLES_FILE, "r", encoding="utf-8") as f:
            articles = json.load(f)
        print(f"Loaded {len(articles)} cleaned articles")
        return articles
    except FileNotFoundError:
        print(f"Error: {CLEANED_ARTICLES_FILE} not found.")
        return []


def load_user_profile():
    try:
        with open(PROFILE_FILE, "r", encoding="utf-8") as f:
            profile = json.load(f)
        return profile
    except FileNotFoundError:
        return {"liked_articles": [], "disliked_articles": []}


def save_user_profile(profile):
    with open(PROFILE_FILE, "w", encoding="utf-8") as f:
        json.dump(profile, f, indent=2, ensure_ascii=False)
    print("User profile updated and saved.")


def get_user_profile_vector(user_interests, liked_articles, vectorizer):
    """Combine user input + liked article contents into one profile vector"""
    profile_texts = [user_interests.lower()]
    
    # add contents from liked article
    for liked_url in liked_articles:
        for article in liked_articles:
            if article["url"] == liked_url:
                profile_texts.append(article["clean_content"])
                break
    
    if len(profile_texts) == 1:
        return vectorizer.transform(profile_texts)
    
    #Avg the vectors of interests and liked contents
    vectors = vectorizer.transform(profile_texts)
    avg_vector = np.mean(vectors.toarray(), axis=0)
    return avg_vector.reshape(1, -1)


def get_recommendations(user_interests: str, articles, top_n=5):
    if not articles:
        return []

    documents = [a["clean_content"] for a in articles if a["clean_content"].strip()]
    if not documents:
        return []

    vectorizer = TfidfVectorizer(max_features=5000, min_df=1)
    tfidf_matrix = vectorizer.fit_transform(documents)

    profile = load_user_profile()
    liked_urls = profile.get("liked_articles", [])

    #
    if liked_urls:
        user_vector = get_user_profile_vector(user_interests, articles, vectorizer)
    else:
        user_vector = vectorizer.transform([user_interests.lower()])

    similarities = cosine_similarity(user_vector, tfidf_matrix).flatten()

    top_indices = similarities.argsort()[-top_n*2:][::-1]

    recommendations = []
    seen_urls = set()

    for idx in top_indices:
        if len(recommendations) >= top_n:
            break
        score = similarities[idx]
        if score <= 0:
            continue
        article = articles[idx]
        url = article["url"]
        if url in seen_urls:
            continue
        seen_urls.add(url)

        recommendations.append({
            "title": article["title"],
            "source": article["source"],
            "url": url,
            "similarity_score": round(float(score), 4),
            "clean_content_preview": article["clean_content"][:150] + "..."
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
    while True:
        articles = load_cleaned_articles()
        if not articles:
            print("No articles found.")
            break

        profile = load_user_profile()
        liked_urls = set(profile.get("liked_articles", []))
        disliked_urls = set(profile.get("disliked_articles", []))

        print(f"Liked articles so far: {len(liked_urls)}")
        print(f"Disliked articles so far: {len(disliked_urls)}")

        print("\nOptions:")
        print("  1. Recommend based on interests / history")
        print("  2. Fetch fresh news articles now")
        print("  3. Show liked articles")
        print("  4. Quit")

        choice = input("\nChoose (1-4): ").strip()

        if choice == "4":
            print("exiting..")
            break

        elif choice == "2":
            print("Running fetch_news.py ...")
            import subprocess
            subprocess.run(["python", "fetch_news.py"])
            print("Fresh fetch done.")
            continue

        elif choice == "3":
            if liked_urls:
                print("\nliked articles:")
                for url in liked_urls:
                    for art in articles:
                        if art["url"] == url:
                            print(f"- {art['title'][:80]}...")
                            print(f"  {art['url'][:60]}...")
                            break
            else:
                print("No liked articles yet.")
            continue

        elif choice == "1":
            user_input = input("\nEnter interests (or press Enter to use history only): ").strip()


            filtered_articles = [
                a for a in articles
                if a["url"] not in liked_urls and a["url"] not in disliked_urls
            ]

            if not filtered_articles:
                print("No new articles left to recommend (all seen or liked/disliked)")
                continue

            recs = get_recommendations(user_input, filtered_articles)

            show_recommendations(recs)

            # Feedback
            if recs:
                print("\nGive feedback (l = like, d = dislike, s = skip):")
                for rec in recs:
                    choice = input(f"\n{rec['title'][:60]}... → (l/d/s): ").strip().lower()
                    url = rec["url"]
                    if choice == 'l':
                        if url not in profile["liked_articles"]:
                            profile["liked_articles"].append(url)
                            print("Liked!")
                    elif choice == 'd':
                        if url not in profile["disliked_articles"]:
                            profile["disliked_articles"].append(url)
                            print("Disliked.")


                save_user_profile(profile)
        else:
            print("Invalid choice. Try again.")


if __name__ == "__main__":
    main()