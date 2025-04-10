import os
import feedparser
from transformers import pipeline
import torch
from googletrans import Translator

def fetch_news():
    rss_url = "https://news.google.com/rss/search?q=warren+buffett+buying"
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

def preprocess_text(text):
    # 불필요한 부분 제거
    text = text.replace("\n", " ").replace("\r", " ")
    return text

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
    
    # 텍스트를 더 작은 조각으로 나누기
    def split_text_for_model(text, max_length=64):  # max_length 값을 64로 줄임
        tokens = text.split()
        chunks = []
        for i in range(0, len(tokens), max_length):
            chunk = tokens[i:i + max_length]
            if len(chunk) > max_length:
                chunk = chunk[:max_length]
            chunks.append(' '.join(chunk))
        return chunks

    translated_news_chunks = split_text_for_model(text)
    
    # 요약의 길이를 조절하여 전체 토큰 수를 줄임
    summaries = [summarizer(chunk, max_length=10, min_length=5, do_sample=False) for chunk in translated_news_chunks]
    summary = ' '.join([result[0]['summary_text'] for result in summaries])
    
    return summary

def save_summary_to_file(summary):
    os.makedirs("api", exist_ok=True)
    with open("api/latest.js", "w", encoding="utf-8") as f:
        f.write(f"export const summary = `{summary}`;\n")  # Corrected line

