from newsapi import NewsApiClient
import json
from datetime import datetime, timedelta
import logging
from database import get_topics, add_news_items

import os

# Get the directory of the current script
current_dir = os.path.dirname(os.path.abspath(__file__))
# Set the path for the log file
log_path = os.path.join(current_dir, 'scraper.log')

# Configure logging
logging.basicConfig(
    filename='scraper.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filemode='a'
)

# Initialize News API client
# Replace 'YOUR_API_KEY' with your actual News API key
newsapi = NewsApiClient(api_key='143b510dd7304b21981f0763eb262c0d')

def scrape_news():
    topics = get_topics()
    news_items = []

    logging.info(f"Scraping news for topics: {topics}")

    for topic in topics:
        topic_name = topic['name']  # Extract the topic name from the dictionary
        try:
            from_date = (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d')
            to_date = datetime.now().strftime('%Y-%m-%d')
            response = newsapi.get_everything(q=topic_name,
                                              language='en',
                                              sort_by='relevancy',
                                              page_size=10,
                                              from_param=from_date,
                                              to=to_date)
            
            for article in response['articles']:
                news_items.append({
                    "topic": topic_name,
                    "title": article['title'],
                    "link": article['url'],
                    "source": article['source']['name'],
                    "published_at": article['publishedAt'],
                    "description": article['description']
                })
            
            logging.info(f"Successfully fetched {len(response['articles'])} articles for topic: {topic}")
        except Exception as e:
            logging.error(f"Error fetching news for topic {topic}: {e}")

    add_news_items(news_items)

    return news_items

def get_news():
    try:
        news = scrape_news()
        return json.dumps(news, indent=2, default=str)
    except Exception as e:
        logging.error(f"Error in get_news: {e}")
        return json.dumps({"error": "An error occurred while fetching news"})

if __name__ == "__main__":
    print(get_news())
    