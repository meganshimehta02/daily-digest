import feedparser
import json
from datetime import datetime, timezone

FEEDS = {
    "BBC World": "https://feeds.bbci.co.uk/news/world/rss.xml",
    "BBC Business": "https://feeds.bbci.co.uk/news/business/rss.xml",
    "BBC Technology": "https://feeds.bbci.co.uk/news/technology/rss.xml",
    "The Guardian World": "https://www.theguardian.com/world/rss",
    "The Guardian Business": "https://www.theguardian.com/business/rss",
    "Al Jazeera": "https://www.aljazeera.com/xml/rss/all.xml",
}

def collect_news():
    articles = []

    for source, url in FEEDS.items():
        print(f"Collecting from {source}...")

        try:
            feed = feedparser.parse(url)

            for entry in feed.entries[:20]:
                articles.append({
                    "source": source,
                    "title": entry.get("title", ""),
                    "link": entry.get("link", ""),
                    "published": entry.get("published", ""),
                    "summary": entry.get("summary", "")
                })

        except Exception as error:
            print(f"Could not collect from {source}: {error}")

    unique_articles = {
        article["link"]: article
        for article in articles
        if article["link"]
    }

    result = {
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "total_articles": len(unique_articles),
        "articles": list(unique_articles.values())
    }

    with open("news_data.json", "w", encoding="utf-8") as file:
        json.dump(result, file, indent=2, ensure_ascii=False)

    print(f"Collected {len(unique_articles)} unique articles.")

if __name__ == "__main__":
    collect_news()
