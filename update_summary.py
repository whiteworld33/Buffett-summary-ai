import feedparser
from transformers import pipeline
import torch

def fetch_news():
    """워런 버핏 관련 뉴스 RSS에서 기사들을 가져옵니다"""
    rss_url = "https://news.google.com/rss/search?q=워런+버핏"
    feed = feedparser.parse(rss_url)
    
    entries = feed.entries[:5]  # 최근 뉴스 5개만 사용
    text = ""
    for entry in entries:
        text += entry.title + ". " + entry.summary + "\n\n"
    return text

def split_text(text, max_tokens=1000):
    """긴 텍스트를 모델이 허용하는 토큰 수 이하로 분할"""
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
    """텍스트를 요약합니다 (여러 청크로 분리한 뒤 요약)"""
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
    """요약된 텍스트를 latest.js 파일로 저장합니다"""
    with open("ai/latest.js", "w", encoding="utf-8") as f:
        f.write(f"export const summary = `{summary}`;\n")

# 실행
news = fetch_news()
summary = summarize(news)
save_summary_to_file(summary)
