import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

API_KEY = os.getenv("GROQ_API_KEY")

if not API_KEY or API_KEY.startswith("YOUR_"):
    raise ValueError("GROQ_API_KEY not found in .env file!")

client = Groq(api_key=API_KEY)

def generate_summary(article_text: str, focus: str = "key facts") -> str:
    """
    Generate a short summary using Groq (Llama-3.3-70B or Mixtral)
    """
    if not article_text or len(article_text.strip()) < 20:
        return "No sufficient content available for summarization."

    prompt = f"""
    You are a helpful news assistant. 
    Summarize the following news article in **3 to 4 clear sentences**.
    Focus mainly on: {focus}.
    Keep it neutral, factual, and easy to understand.
    Do not add opinions.

    Article:
    {article_text}
    """

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=300,
        )
        summary = response.choices[0].message.content.strip()
        return summary
    except Exception as e:
        return f"⚠️ Summary generation failed: {str(e)}"


if __name__ == "__main__":
    print("Groq Summarizer is ready!\n")
    
    test_text = "India successfully launched its first privately developed rocket into space. The launch marks a new milestone for the country's growing private space industry and opens doors for commercial satellite deployments."
    
    print("Test Article:")
    print(test_text)
    print("\nGenerated Summary:")
    print(generate_summary(test_text))