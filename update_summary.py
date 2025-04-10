import os
import feedparser
from transformers import pipeline
import torch
from googletrans import Translator

def fetch_news():
    rss_url = "https://news.google.com/rss/search?q=워런+버핏"
    feed = feedparser.parse(rss_url)
    entries = feed.entries[:5]
    text = ""
    for entry in entries:
        text += entry.title + ". " + entry.summary + "\n\n"
    return text

def translate_text(text, dest_language="ko"):
    translator = Translator()
    translated = translator.translate(text, dest=dest_language)
    return translated.text

def split_text(text, max_tokens=300):  # max_tokens 값을 더 줄임
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
        if len(chunk.split()) > 10:  # 너무 짧은 텍스트는 요약하지 않음
            result = summarizer(chunk, max_length=80, min_length=30, do_sample=False)  # max_length 값을 더 줄임
            results.append(result[0]['summary_text'])
        else:
            results.append(chunk)
    return "\n\n".join(results)

def save_summary_to_file(summary):
    os.makedirs("api", exist_ok=True)
    with open("api/latest.js", "w", encoding="utf-8") as f:
        f.write(f"export const summary = `{summary}`;\n")

# 실행
news = fetch_news()
translated_news = translate_text(news)
summary = summarize(translated_news)
save_summary_to_file(summary)
