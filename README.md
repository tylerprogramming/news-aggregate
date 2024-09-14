# AI News Aggregator

This project is an AI News Aggregator that scrapes news articles from various sources, stores them in a database, and provides a web interface to view and interact with the news items.

## Features

- Scrapes news articles from multiple sources using the News API
- Stores news articles in a SQLite database
- Provides a web interface to view and interact with news articles
- Allows sorting and filtering of news articles
- Implements a random article selection feature
- Sends emails with selected news articles

## Project Structure

- `app.py`: Main Flask application file
- `database.py`: Database models and operations
- `scraper.py`: News scraping functionality
- `scheduler.py`: Scheduled tasks for periodic news updates
- `utility.py`: Utility functions, including email sending
- `templates/index.html`: Main HTML template for the web interface

## How It Works

1. **News Scraping**: 
   - The `scraper.py` file uses the News API to fetch articles on various AI-related topics.
   - Scraped articles are stored in the SQLite database using models defined in `database.py`.

2. **Scheduled Updates**:
   - `scheduler.py` sets up periodic tasks to update the news database at regular intervals.

3. **Web Interface**:
   - `app.py` sets up a Flask web server that renders the `index.html` template.
   - Users can view news articles, sort them by different criteria, and adjust the number of displayed items.

4. **Random Articles**:
   - Users can request random articles, which are fetched from the database and displayed in a modal.

5. **Email Functionality**:
   - Users can send selected articles via email using the "Send Email" feature.
   - The `utility.py` file handles the email sending functionality.

6. **Article Usage Tracking**:
   - The application tracks which articles have been used (e.g., sent in emails) to avoid repetition.

## Setup and Running

1. Install required dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Set up your News API key in `scraper.py`.

3. Run the Flask application:
   ```
   python app.py
   ```

4. Access the web interface at `http://localhost:5001`.

## Note

This project is designed for educational purposes and may require additional security measures before deployment in a production environment.