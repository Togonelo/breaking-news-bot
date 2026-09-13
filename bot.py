import requests
import os
import time
import sys
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Your API keys and webhook
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")
CONGRESS_API_KEY = os.getenv("CONGRESS_API_KEY")
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")

# Congress.gov API base URL
CONGRESS_BASE_URL = "https://api.congress.gov/v3"

def send_to_discord(message):
    """Send a message to Discord webhook"""
    data = {"content": message}
    response = requests.post(DISCORD_WEBHOOK, json=data)
    if response.status_code == 204:
        print(f"✓ Sent to Discord: {message[:50]}...")
    else:
        print(f"✗ Failed to send: {response.status_code}")

def get_breaking_news():
    """Fetch breaking news from NewsAPI"""
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": "breaking OR emergency OR congress OR senate OR house",
        "sortBy": "publishedAt",
        "language": "en",
        "apiKey": NEWSAPI_KEY,
        "pageSize": 5
    }
    
    try:
        response = requests.get(url, params=params)
        articles = response.json().get("articles", [])
        
        if articles:
            top_article = articles[0]
            headline = top_article["title"]
            source = top_article["source"]["name"]
            url = top_article["url"]
            
            message = f"🔴 **BREAKING**: {headline}\n📰 {source}\n🔗 {url}"
            send_to_discord(message)
    except Exception as e:
        print(f"Error fetching news: {e}")

def get_congress_activity():
    """Fetch recent Congressional activity"""
    url = f"{CONGRESS_BASE_URL}/bill"
    params = {
        "api_key": CONGRESS_API_KEY,
        "limit": 5,
        "sort": "-updateDate"
    }
    
    try:
        response = requests.get(url, params=params)
        bills = response.json().get("results", [])
        
        if bills:
            bill = bills[0]
            bill_number = bill["number"]
            title = bill["title"]
            latest_action = bill.get("latestAction", {}).get("actionDate", "N/A")
            
            message = f"📜 **Congress Activity**: {bill_number} - {title}\n📅 Latest: {latest_action}"
            send_to_discord(message)
    except Exception as e:
        print(f"Error fetching Congress data: {e}")

def run_once():
    """Run the bot once (for testing)"""
    print(f"🧪 TEST MODE - Running once")
    print(f"Discord Webhook: {DISCORD_WEBHOOK[:30]}...")
    
    get_breaking_news()
    get_congress_activity()
    
    print("✓ Test complete!")

def main():
    """Main loop - runs every 10 minutes"""
    print(f"🤖 Bot started at {datetime.now()}")
    print(f"Discord Webhook: {DISCORD_WEBHOOK[:30]}...")
    
    while True:
        try:
            print(f"\n[{datetime.now()}] Checking for updates...")
            
            get_breaking_news()
            get_congress_activity()
            
            # Wait 10 minutes before checking again
            time.sleep(600)
            
        except Exception as e:
            print(f"Error in main loop: {e}")
            time.sleep(60)

if __name__ == "__main__":
    # Check if test mode is enabled
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        run_once()
    else:
        main()
