
import feedparser
import json
import re
import time
import html
from datetime import datetime, timezone
from urllib.request import Request, urlopen
from urllib.parse import quote_plus, urlsplit, urlunsplit, parse_qsl, urlencode

OUTPUT_FILE = "news_data.json"
MAX_ARTICLES_PER_FEED = 15

# ==================================================
# DIRECT RSS SOURCES
# ==================================================

FEEDS = [
    # GENERAL NEWS
    {
        "name": "BBC World",
        "url": "https://feeds.bbci.co.uk/news/world/rss.xml",
        "categories": ["Geopolitics", "World"]
    },
    {
        "name": "BBC Business",
        "url": "https://feeds.bbci.co.uk/news/business/rss.xml",
        "categories": ["Business", "Finance"]
    },
    {
        "name": "BBC Technology",
        "url": "https://feeds.bbci.co.uk/news/technology/rss.xml",
        "categories": ["Technology", "AI"]
    },
    {
        "name": "The Guardian World",
        "url": "https://www.theguardian.com/world/rss",
        "categories": ["Geopolitics", "World"]
    },
    {
        "name": "The Guardian Business",
        "url": "https://www.theguardian.com/business/rss",
        "categories": ["Business", "Finance"]
    },
    {
        "name": "The Guardian Technology",
        "url": "https://www.theguardian.com/technology/rss",
        "categories": ["Technology", "AI"]
    },
    {
        "name": "Al Jazeera",
        "url": "https://www.aljazeera.com/xml/rss/all.xml",
        "categories": ["Geopolitics", "World"]
    },
    {
        "name": "Deutsche Welle",
        "url": "https://rss.dw.com/rdf/rss-en-all",
        "categories": ["Geopolitics", "World"]
    },
    {
        "name": "NPR World",
        "url": "https://feeds.npr.org/1004/rss.xml",
        "categories": ["World", "Geopolitics"]
    },
    {
        "name": "France 24",
        "url": "https://www.france24.com/en/rss",
        "categories": ["Geopolitics", "World"]
    },

    # BUSINESS AND FINANCE
    {
        "name": "CNBC",
        "url": "https://www.cnbc.com/id/10001147/device/rss/rss.html",
        "categories": ["Business", "Finance"]
    },

    # TECHNOLOGY AND STARTUPS
    {
        "name": "TechCrunch",
        "url": "https://techcrunch.com/feed/",
        "categories": ["Technology", "Startups", "Entrepreneurship"]
    },
    {
        "name": "The Verge",
        "url": "https://www.theverge.com/rss/index.xml",
        "categories": ["Technology", "AI"]
    },
    {
        "name": "MIT Technology Review",
        "url": "https://www.technologyreview.com/feed/",
        "categories": ["Technology", "AI"]
    },

    # MARKETING AND HR
    {
        "name": "Marketing Dive",
        "url": "https://www.marketingdive.com/feeds/news/",
        "categories": ["Marketing", "PR"]
    },
    {
        "name": "HR Dive",
        "url": "https://www.hrdive.com/feeds/news/",
        "categories": ["HR", "Business"]
    },

    # INTERNATIONAL ORGANISATIONS
    {
        "name": "UN News",
        "url": "https://news.un.org/feed/subscribe/en/news/all/rss.xml",
        "categories": ["Geopolitics", "World"]
    },

    # INDIA
    {
        "name": "Indian Express",
        "url": "https://indianexpress.com/section/india/feed/",
        "categories": ["India", "Politics"]
    },
    {
        "name": "Livemint",
        "url": "https://www.livemint.com/rss/news",
        "categories": ["India", "Business", "Finance"]
    },
]

# ==================================================
# GOOGLE NEWS RSS DISCOVERY
# ==================================================

GOOGLE_NEWS_QUERIES = [
    {
        "name": "Reuters",
        "query": "site:reuters.com geopolitics OR business OR finance",
        "categories": ["Geopolitics", "Business", "Finance"]
    },
    {
        "name": "Associated Press",
        "query": "site:apnews.com world OR business OR technology",
        "categories": ["World", "Business", "Technology"]
    },
    {
        "name": "Geopolitics",
        "query": "geopolitics diplomacy international relations sanctions",
        "categories": ["Geopolitics", "World"]
    },
    {
        "name": "Global Finance",
        "query": "global finance stock markets central banks interest rates",
        "categories": ["Finance", "Economics"]
    },
    {
        "name": "Business Strategy",
        "query": "business strategy corporate acquisitions restructuring",
        "categories": ["Business", "Strategy"]
    },
    {
        "name": "Startups",
        "query": "startups venture capital startup funding entrepreneurship",
        "categories": ["Startups", "Entrepreneurship"]
    },
    {
        "name": "Marketing",
        "query": "marketing campaigns brand strategy consumer behaviour advertising",
        "categories": ["Marketing", "Consumer Psychology"]
    },
    {
        "name": "Public Relations",
        "query": "public relations corporate communications brand reputation crisis communication",
        "categories": ["PR", "Communications"]
    },
    {
        "name": "Human Resources",
        "query": "human resources workplace culture layoffs talent management",
        "categories": ["HR", "Leadership"]
    },
    {
        "name": "Fashion and Luxury",
        "query": "fashion industry luxury brands fashion business acquisitions",
        "categories": ["Fashion", "Luxury", "Business"]
    },
    {
        "name": "Artificial Intelligence",
        "query": "artificial intelligence AI companies technology industry",
        "categories": ["Technology", "AI"]
    },
    {
        "name": "India Business",
        "query": "India business Indian economy Indian startups Indian markets",
        "categories": ["India", "Business", "Finance"]
    },
    {
        "name": "Global Economy",
        "query": "global economy inflation trade policy economic growth",
        "categories": ["Economics", "Finance"]
    },
    {
        "name": "Consumer Brands",
        "query": "consumer brands retail industry brand launches consumer trends",
        "categories": ["Marketing", "Business"]
    },
    {
        "name": "Think with Google",
        "query": "site:thinkwithgoogle.com marketing consumer insights",
        "categories": ["Marketing", "Consumer Psychology"]
    },
    {
        "name": "Harvard Business Review",
        "query": "site:hbr.org leadership management business strategy",
        "categories": ["Business", "HR", "Leadership"]
    },
    {
        "name": "War on the Rocks",
        "query": "site:warontherocks.com military strategy geopolitics",
        "categories": ["Geopolitics", "Security"]
    },
    {
        "name": "Fashion Business",
        "query": "site:voguebusiness.com OR site:businessoffashion.com fashion luxury",
        "categories": ["Fashion", "Luxury", "Business"]
    },
    {
        "name": "India Economy",
        "query": "India RBI economy inflation monetary policy",
        "categories": ["India", "Finance", "Economics"]
    }
]

for item in GOOGLE_NEWS_QUERIES:
    url = (
        "https://news.google.com/rss/search?q="
        + quote_plus(item["query"] + " when:7d")
        + "&hl=en-IN&gl=IN&ceid=IN:en"
    )

    FEEDS.append({
        "name": "Google News - " + item["name"],
        "url": url,
        "categories": item["categories"],
        "google_news": True
    })


# ==================================================
# CLEANING FUNCTIONS
# ==================================================

def clean_text(value):
    if not value:
        return ""

    value = html.unescape(str(value))
    value = re.sub(r"<[^>]+>", " ", value)
    value = re.sub(r"\s+", " ", value)

    return value.strip()


def clean_url(url):
    if not url:
        return ""

    parts = urlsplit(url)

    tracking = {
        "utm_source", "utm_medium", "utm_campaign",
        "utm_term", "utm_content", "fbclid", "gclid"
    }

    query = [
        (key, value)
        for key, value in parse_qsl(parts.query)
        if key.lower() not in tracking
    ]

    return urlunsplit((
        parts.scheme,
        parts.netloc,
        parts.path,
        urlencode(query),
        ""
    ))


def get_published(entry):
    return entry.get("published") or entry.get("updated") or ""


def get_publisher(entry, feed):
    source = entry.get("source", {})
    publisher = source.get("title", "") if source else ""

    if publisher:
        return clean_text(publisher)

    return feed["name"]


# ==================================================
# NEWS COLLECTION
# ==================================================

def collect_news():

    articles = {}
    successful_feeds = []
    failed_sources = []

    print("Starting The Intelligence Room collection")
    print("Feeds to check:", len(FEEDS))

    for feed in FEEDS:

        name = feed["name"]

        print("\nChecking:", name)

        try:
            request = Request(
                feed["url"],
                headers={
                    "User-Agent": "Mozilla/5.0 IntelligenceRoom/1.0"
                }
            )

            with urlopen(request, timeout=25) as response:
                content = response.read()

            parsed = feedparser.parse(content)

            entries = parsed.entries[:MAX_ARTICLES_PER_FEED]

            if not entries:
                failed_sources.append({
                    "source": name,
                    "reason": "No articles returned"
                })
                print("No articles found")
                continue

            successful_feeds.append(name)

            collected = 0

            for entry in entries:

                title = clean_text(entry.get("title", ""))
                original_link = entry.get("link", "")
                link = clean_url(original_link)

                if not title or not link:
                    continue

                publisher = get_publisher(entry, feed)
                summary = clean_text(
                    entry.get("summary", "")
                    or entry.get("description", "")
                )

                categories = feed["categories"]

                if link in articles:

                    existing = articles[link]

                    existing["categories"] = sorted(
                        set(existing["categories"] + categories)
                    )

                    existing["sources"] = sorted(
                        set(existing["sources"] + [publisher])
                    )

                    if not existing["summary"] and summary:
                        existing["summary"] = summary

                    continue

                articles[link] = {
                    "source": publisher,
                    "sources": [publisher],
                    "title": title,
                    "link": link,
                    "original_link": original_link,
                    "published": get_published(entry),
                    "summary": summary,
                    "categories": categories,
                    "analysis_status": "Pending"
                }

                collected += 1

            print("Articles added:", collected)

        except Exception as error:

            failed_sources.append({
                "source": name,
                "reason": str(error)[:250]
            })

            print("Source failed:", str(error)[:150])

        time.sleep(0.3)

    # ==================================================
    # REPORT AND STATISTICS
    # ==================================================

    article_list = list(articles.values())

    publishers = sorted({
        source
        for article in article_list
        for source in article["sources"]
    })

    category_counts = {}

    for article in article_list:
        for category in article["categories"]:
            category_counts[category] = (
                category_counts.get(category, 0) + 1
            )

    report = {
        "publication": "The Intelligence Room",
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "total_articles": len(article_list),
        "total_feeds": len(FEEDS),
        "successful_feeds": len(successful_feeds),
        "failed_feed_count": len(failed_sources),
        "total_sources": len(publishers),
        "publishers": publishers,
        "successful_sources": successful_feeds,
        "failed_sources": failed_sources,
        "category_counts": category_counts,
        "articles": article_list
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(report, file, indent=2, ensure_ascii=False)

    print("\n================================")
    print("THE INTELLIGENCE ROOM")
    print("COLLECTION COMPLETE")
    print("================================")
    print("Total articles:", len(article_list))
    print("Feeds checked:", len(FEEDS))
    print("Successful feeds:", len(successful_feeds))
    print("Failed feeds:", len(failed_sources))
    print("Unique publishers:", len(publishers))
    print("Category counts:", category_counts)
    print("================================")


if __name__ == "__main__":
    collect_news()

