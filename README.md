# NewsIO – Personalized News Recommendation System

**NewsIO** is a **personalized news recommender** built from scratch in Python.  
It fetches real news articles(From NewsAPI), cleans the text, and recommends articles that match **user interests** (keywords like "AI, cricket, India").  

Over time, when user **like** or **dislike** articles, the system learns user preferences and gives better suggestions.

This is a complete beginner-to-intermediate **machine learning project** using **content-based filtering** — no external datasets or complex deep learning used.

## Core Science & Machine Learning

NewsIO uses **content-based recommendation** — it recommends articles based on **what the articles are about**, not what other people read.

### 1. TF-IDF (Term Frequency – Inverse Document Frequency)

- Turns text (title + description) into numbers (vectors).
- **Term Frequency (TF)**: How often a word appears in one article.  
  More times = more important **in that article**.
- **Inverse Document Frequency (IDF)**: How rare the word is across **all** articles.  
  Common words like "the", "is", "and" get very low weight.  
  Rare/important words like "AI", "cricket", "Modi" get high weight.
- **TF-IDF score** = TF × IDF -> gives every word a smart importance score.
- Result: Each article becomes a long list of numbers (vector) where important words have big values.

### 2. Cosine Similarity

- After TF-IDF, Compare user interests (also turned into a TF-IDF vector) with every article vector.
- **Cosine Similarity** measures how similar two vectors are by looking at the **angle** between them (not length).
  - Score = 1.0 -> almost identical (perfect match)
  - Score = 0.0 -> completely different
  - Score close to 0 -> unrelated
- Formula used:  
  cos(θ) = (A · B) / (||A|| × ||B||)  
  → Simple: higher score = more similar direction in word-space.

This is why it recommends articles with similar **topics/keywords**, even if titles are different.

### 3. Personalization with Feedback (Like / Dislike)

- When user **like** an article, then its content gets added to user "profile vector" (averaged with user keywords).
- Future recommendations get **boosted** toward similar topics.
- Disliked articles are remembered (currently just filtered out — can be improved to reduce similarity later).

This is a simple form of **implicit feedback learning** — the system slowly tunes itself to user taste without needing complex models.

→ All done with **scikit-learn**

## Features
- Fetch real news via NewsAPI (broad or keyword-based)
- Clean text: lowercase, remove punctuation/stopwords/numbers
- Interactive CLI menu: recommend, fetch fresh, show likes, quit
- Like/dislike feedback → improves recommendations over time
- Saves your profile in `user_profile.json`

## Tech Stack
- Python 3
- requests (API calls)
- pandas, numpy
- scikit-learn (TF-IDF + cosine_similarity)
- json (save/load data)

## How to Run (Step by Step)

1. Clone the repository
   ```bash
   git clone https://github.com/cmshebeeb/newsio.git
   cd newsio
2. Create and activate virtual environment
    python -m venv .venv
    .venv\Scripts\activate
3. Install dependencies
    pip install -r requirements.txt
4. Get free NewsAPI key
    Go to https://newsapi.org/
    Sign up and copy API key
    Paste it inside fetch_news.py (replace "API_KEY")
5. Initial Setup – Creating the Data Files

**Important:** The following JSON files are **not** committed to the repository (they are ignored via `.gitignore`):

- `data/articles.json` – raw articles from NewsAPI
- `data/cleaned_articles.json` – processed & cleaned articles
- `data/user_profile.json` – your likes/dislikes (created automatically)

    Need to generate them the first time:

    # 1. Download some news articles
    python fetch_news.py

    # 2. Clean the text & prepare for ML
    python preprocess.py

    # 3. Run the recommender at least once
    #    → it will create an empty automatically
            python recommend.py