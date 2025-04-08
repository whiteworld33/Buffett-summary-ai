import feedparser
from transformers import pipeline

def fetch_news():
    rss_url = "https://news.google.com/rss/search?q=워런+버핏"
    feed = feedparser.parse(rss_url)
    articles = [entry["title"] + " - " + entry["summary"] for entry in feed["entries"][:5]]
    return " ".join(articles)

from transformers import pipeline
import torch

def split_text(text, max_tokens=1000):
    """토큰 수 기준으로 긴 텍스트를 나누는 함수"""
    sentences = text.split(". ")
    chunks = []
    current_chunk = ""

    for sentence in sentences:
        if len(current_chunk + sentence) > max_tokens:
            chunks.append(current_chunk.strip())
            current_chunk = sentence + ". "
        else:
            current_chunk += sentence + ". "

    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks

def summarize(text):
    device = 0 if torch.cuda.is_available() else -1
    print("Device set to use", "cuda" if device == 0 else "cpu")

    summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6", device=device)

    chunks = split_text(text, max_tokens=1000)
    results = []

    for chunk in chunks:
        result = summarizer(chunk, max_length=200, min_length=50, do_sample=False)
        results.append(result[0]['summary_text'])

    return "\n\n".join(results)
if __name__ == "__main__":
    news = fetch_news()
    summary = summarize(news)
    
    with open("latest.js", "w") as f:
        f.write(f"export const summary = `{summary}`;")
