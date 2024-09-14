from flask import Flask, jsonify, render_template, request
from database import get_latest_news, get_topic_stats, toggle_article_used, add_news_items, get_random_articles_by_topic, get_random_articles_html, get_topics, add_topic, remove_topic
from scraper import scrape_news
import logging
from utility import send_email
from datetime import datetime

app = Flask(__name__)

# Configure logging
logging.basicConfig(
    filename='scraper.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filemode='a'
)

@app.route('/', methods=['GET'])
def index():
    try:
        item_count = int(request.args.get('item_count', 20))
        sort_by = request.args.get('sort_by', 'published_at')
        
        latest_news = get_latest_news(limit=item_count, sort_by=sort_by)
        topic_stats = get_topic_stats()
        
        return render_template('index.html', 
                               news_items=latest_news, 
                               topic_stats=topic_stats, 
                               item_count=item_count, 
                               sort_by=sort_by)
    except Exception as e:
        logging.error(f"Error fetching news: {e}")
        return render_template('index.html', error="An error occurred while fetching news")

@app.route('/news', methods=['GET'])
def news():
    try:
        latest_news = get_latest_news()
        return jsonify(latest_news)
    except Exception as e:
        logging.error(f"Error fetching news: {e}")
        return jsonify({"error": "An error occurred while fetching news"}), 500

@app.route('/update', methods=['POST'])
def update_news():
    try:
        
        news_items = scrape_news()
        add_news_items(news_items)
        return jsonify({"message": "News updated successfully"}), 200
    except Exception as e:
        logging.error(f"Error updating news: {e}")
        return jsonify({"error": "An error occurred while updating news"}), 500

@app.route('/toggle_used', methods=['POST'])
def toggle_used():
    try:
        data = request.json
        article_id = data['id']
        is_used = data['is_used']
        
        success = toggle_article_used(article_id, is_used)
        return jsonify({"success": success})
    except Exception as e:
        logging.error(f"Error toggling article used status: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/random_articles', methods=['GET'])
def random_articles():
    try:
        random_articles = get_random_articles_by_topic()
        return jsonify(random_articles)
    except Exception as e:
        logging.error(f"Error fetching random articles: {e}")
        return jsonify({"error": "An error occurred while fetching random articles"}), 500

@app.route('/send_email', methods=['POST'])
def send_email_route():
    try:
        data = request.json
        recipient = data['recipient']
        subject = data['subject']
        
        # Generate HTML content and mark articles as used
        html_content = get_random_articles_html()
        
        send_email(recipient, subject, html_content)
        return jsonify({"message": "Email sent successfully!"}), 200
    except Exception as e:
        logging.error(f"Error sending email: {e}")
        return jsonify({"error": "An error occurred while sending the email"}), 500

@app.route('/manage_topics', methods=['GET'])
def manage_topics():
    topics = get_topics()
    return render_template('manage_topics.html', topics=topics)

@app.route('/add_topic', methods=['POST'])
def add_topic_route():
    data = request.json
    topic = data['topic']
    success = add_topic(topic)
    return jsonify({"success": success})

@app.route('/remove_topic', methods=['POST'])
def remove_topic_route():
    data = request.json
    topic = data['topic']
    success = remove_topic(topic)
    return jsonify({"success": success})

@app.route('/newsletter_editor', methods=['GET', 'POST'])
def newsletter_editor():
    if request.method == 'POST':
        html_content = request.form['content']
        # Here you would typically save the content or send it as an email
        # For now, we'll just return a success message
        return jsonify({'success': True, 'message': 'Newsletter saved successfully'})
    return render_template('newsletter_editor.html')

if __name__ == '__main__':
    logging.info("Starting Flask app...")
    app.run(debug=True, host='0.0.0.0', port=5001)