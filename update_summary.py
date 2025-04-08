import feedparser
from transformers import pipeline

def fetch_news():
    rss_url = "https://news.google.com/rss/search?q=워런+버핏"
    feed = feedparser.parse(rss_url)
    articles = [entry["title"] + " - " + entry["summary"] for entry in feed["entries"][:5]]
    return " ".join(articles)

def summarize(text):
    summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")
    result = summarizer(text, max_length=200, min_length=50, do_sample=False)
    return result[0]['summary_text']

if __name__ == "__main__":
    news = fetch_news()
    summary = summarize(news)
    
    with open("latest.js", "w") as f:
        f.write(f"export const summary = `{summary}`;")
