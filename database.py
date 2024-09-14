from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from sqlalchemy import inspect
import logging
import random
import sqlite3
import os

# Configure logging
logging.basicConfig(filename='scraper.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', filemode='a')

Base = declarative_base()

class NewsItem(Base):
    __tablename__ = 'news_items'

    id = Column(Integer, primary_key=True)
    topic = Column(String)
    title = Column(String)
    link = Column(String)
    source = Column(String)
    published_at = Column(DateTime)
    description = Column(String)
    is_used = Column(Boolean, default=False)

class Topic(Base):
    __tablename__ = 'topics'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)

# Get the directory of the current script
current_dir = os.path.dirname(os.path.abspath(__file__))
# Set the path for the database file
db_path = os.path.join(current_dir, 'news.db')

print(db_path)

def get_db_connection():
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

engine = create_engine(f'sqlite:///{db_path}')
Session = sessionmaker(bind=engine)

def init_db():
    Base.metadata.create_all(engine)
    logging.info("Database initialized")

def add_news_items(items):
    session = Session()
    try:
        added_count = 0
        for item in items:
            # Convert published_at to datetime object if it's a string
            if isinstance(item['published_at'], str):
                item['published_at'] = datetime.strptime(item['published_at'], "%Y-%m-%dT%H:%M:%SZ")
            
            # Check if the item already exists in the database
            existing_item = session.query(NewsItem).filter_by(
                title=item['title'],
                link=item['link'],
                published_at=item['published_at']
            ).first()
            
            if not existing_item:
                news_item = NewsItem(**item)
                session.add(news_item)
                added_count += 1
        
        session.commit()
        logging.info(f"Added {added_count} new news items to the database")
    except Exception as e:
        session.rollback()
        logging.error(f"Error adding news items: {e}")
        raise e
    finally:
        session.close()

def toggle_article_used(article_id, is_used):
    session = Session()
    try:
        article = session.query(NewsItem).filter_by(id=article_id).first()
        if article:
            article.is_used = is_used
            session.commit()
            logging.info(f"Article {article_id} used status updated to {is_used}")
            return True
        else:
            logging.warning(f"Article {article_id} not found")
            return False
    except Exception as e:
        session.rollback()
        logging.error(f"Error updating article used status: {e}")
        return False
    finally:
        session.close()

def get_latest_news(limit=20, sort_by='published_at'):
    session = Session()
    try:
        query = session.query(NewsItem)
        
        if sort_by == 'published_at':
            query = query.order_by(NewsItem.published_at.desc())
        elif sort_by == 'topic':
            query = query.order_by(NewsItem.topic)
        elif sort_by == 'source':
            query = query.order_by(NewsItem.source)
        
        news_items = query.limit(limit).all()
        
        logging.info(f"Retrieved {len(news_items)} latest news items")
        return [
            {
                "id": item.id,
                "topic": item.topic,    
                "title": item.title,
                "link": item.link,
                "source": item.source,
                "published_at": item.published_at.isoformat() if item.published_at else None,
                "description": item.description,
                "is_used": item.is_used
            }
            for item in news_items
        ]
    except Exception as e:
        logging.error(f"Error retrieving latest news: {e}")
        raise e
    finally:
        session.close()

def get_topic_stats():
    session = Session()
    try:
        stats = session.query(
            NewsItem.topic,
            func.count(NewsItem.id).label('total'),
            func.sum(NewsItem.is_used.cast(Integer)).label('used')
        ).group_by(NewsItem.topic).all()
        return [{'topic': s.topic, 'total': s.total, 'used': s.used} for s in stats]
    except Exception as e:
        logging.error(f"Error retrieving topic stats: {e}")
        raise e
    finally:
        session.close()

def get_random_articles_by_topic():
    session = Session()
    try:
        # Get all unique topics
        topics = session.query(NewsItem.topic).distinct().all()
        topics = [topic[0] for topic in topics]

        random_articles = {}
        for topic in topics:
            # Get a random article for each topic
            random_article = session.query(NewsItem).filter_by(topic=topic).order_by(func.random()).first()
            if random_article:
                random_articles[topic] = {
                    'title': random_article.title,
                    'description': random_article.description,
                    'link': random_article.link,
                    'source': random_article.source,
                    'published_at': random_article.published_at.isoformat(),
                    'topic': random_article.topic
                }

        return random_articles
    except Exception as e:
        logging.error(f"Error getting random articles: {e}")
        return {}
    finally:
        session.close()

def get_random_articles_html():
    session = Session()
    try:
        articles = get_random_articles_by_topic()
        
        html_template = """
        <html>
        <body>
        <h1>Today's Random News Articles</h1>
        {article_content}
        </body>
        </html>
        """
        
        article_template = """
        <h2>{topic}</h2>
        <h3><a href="{link}">{title}</a></h3>
        <p>{short_description}</p>
        <hr>
        """
        
        article_content = ""
        for topic, article in articles.items():
            # Shorten the description to 100 characters
            short_description = article['description'][:300] + '...' if len(article['description']) > 100 else article['description']
            
            article_content += article_template.format(**article, short_description=short_description)
            
            # Mark the article as used
            news_item = session.query(NewsItem).filter_by(
                title=article['title'],
                link=article['link'],
                published_at=datetime.fromisoformat(article['published_at'])
            ).first()
            if news_item:
                news_item.is_used = True
        
        session.commit()
        return html_template.format(article_content=article_content)
    except Exception as e:
        session.rollback()
        logging.error(f"Error generating random articles HTML and marking as used: {e}")
        raise
    finally:
        session.close()

def get_topics():
    session = Session()
    try:
        topic_stats = session.query(
            Topic.name,
            func.count(NewsItem.id).label('total_articles'),
            func.sum(NewsItem.is_used.cast(Integer)).label('used_articles')
        ).outerjoin(NewsItem, NewsItem.topic == Topic.name)\
         .group_by(Topic.name)\
         .all()
        
        return [
            {
                'name': topic.name,
                'total_articles': topic.total_articles or 0,
                'used_articles': topic.used_articles or 0,
                'unused_articles': (topic.total_articles or 0) - (topic.used_articles or 0)
            }
            for topic in topic_stats
        ]
    except Exception as e:
        logging.error(f"Error getting topic stats: {e}")
        return []
    finally:
        session.close()

def add_topic(topic_name):
    session = Session()
    try:
        topic = Topic(name=topic_name)
        session.add(topic)
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        logging.error(f"Error adding topic: {e}")
        return False
    finally:
        session.close()

def remove_topic(topic_name):
    session = Session()
    try:
        topic = session.query(Topic).filter_by(name=topic_name).first()
        if topic:
            session.delete(topic)
            session.commit()
            return True
        return False
    except Exception as e:
        session.rollback()
        logging.error(f"Error removing topic: {e}")
        return False
    finally:
        session.close()

init_db()