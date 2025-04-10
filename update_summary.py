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

def split_text(text, max_tokens=100):  # max_tokens 값을 더 줄임
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
    
    # 추가된 코드: 텍스트를 더 작은 조각으로 나누기
    def split_text_for_model(text, max_length=1024):
        tokens = text.split()
        chunks = [tokens[i:i + max_length] for i in range(0, len(tokens), max_length)]
        return [' '.join(chunk) for chunk in chunks]

    translated_news_chunks = split_text_for_model(text)
    summaries = [summarizer(chunk, max_length=30, min_length=20, do_sample=False) for chunk in translated_news_chunks]
    summary = ' '.join([result[0]['summary_text'] for result in summaries])
    
    return summary

def save_summary_to_file(summary):
    os.makedirs("api", exist_ok=True)
    with open("api/latest.js", "w", encoding="utf-8") as f:
        f.write(f"export const summary = `{summary}`;\n")

# 실행
news = fetch_news()
translated_news = translate_text(news)
summary = summarize(translated_news)
save_summary_to_file(summary)
