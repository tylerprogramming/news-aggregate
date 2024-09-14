from apscheduler.schedulers.blocking import BlockingScheduler
from pytz import utc  # Import UTC timezone from pytz
from scraper import scrape_news
from database import add_news_items
import logging

# Configure logging
logging.basicConfig(
    filename='scraper.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def scheduled_scrape():
    try:
        logger.info("Starting scheduled scrape")
        news_items = scrape_news()
        add_news_items(news_items)
        logger.info(f"Scheduled scrape completed. Added {len(news_items)} news items.")
    except Exception as e:
        logger.error(f"Error in scheduled scrape: {e}")

scheduler = BlockingScheduler(timezone=utc)  # Set the scheduler's timezone to UTC
scheduler.add_job(scheduled_scrape, 'interval', hours=12)
scheduler.start()

if __name__ == "__main__":
    try:
        logger.info("Starting scheduler")
        while True:
            pass
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        logger.info("Scheduler stopped")