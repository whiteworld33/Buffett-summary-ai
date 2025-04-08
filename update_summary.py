import os
import feedparser
from transformers import pipeline
import torch

def fetch_news():
    rss_url = "https://news.google.com/rss/search?q=워런+버핏"
    feed = feedparser.parse(rss_url)
    entries = feed.entries[:5]
    text = ""
    for entry in entries:
        text += entry.title + ". " + entry.summary + "\n\n"
    return text

def split_text(text, max_tokens=1000):
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
    chunks = split_text(text)
    results = []
    for chunk in chunks:
        result = summarizer(chunk, max_length=200, min_length=50, do_sample=False)
        results.append(result[0]['summary_text'])
    return "\n\n".join(results)

def save_summary_to_file(summary):
    os.makedirs("api", exist_ok=True)  # <<< 이 줄 추가: 'api' 폴더 없으면 생성
    with open("api/latest.js", "w", encoding="utf-8") as f:
        f.write(f"export const summary = `{summary}`;\n")

# 실행
news = fetch_news()
summary = summarize(news)
save_summary_to_file(summary)
