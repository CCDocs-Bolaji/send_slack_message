import logging
import requests
from bs4 import BeautifulSoup as BS
from datetime import datetime, timedelta
import pytz
from config import (
    USER, PASS, SLACK_CHANNELS, BOLAJI, ALEJANDRO, SLACK_BOT, 
    ROOFCON_USER, ROOFCON_PASS, CORNERSTONE_SLACK_CHANNEL
)

# Configuration for Servers
SERVERS = [
    {
        "name": "CCDOCS",
        "base_url": f"https://{USER}:{PASS}@login.theccdocs.com",
        "channel_mapper": SLACK_CHANNELS,
    },
    {
        "name": "CORNERSTONE",
        "base_url": f"https://{ROOFCON_USER}:{ROOFCON_PASS}@cornerconstruction.ccdocs.com",
        "channel": CORNERSTONE_SLACK_CHANNEL,
    }
]

# Setup logging
logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("list_alert.log"), logging.StreamHandler()]
)

# Timezone settings
est = pytz.timezone('US/Eastern')
thirty_minutes_ago = datetime.now(est) - timedelta(minutes=30)

# Utility Functions
def fetch_rows(server_base_url):
    """Fetch the rows containing records."""
    url = f"{server_base_url}/vicidial/admin.php?ADD=700000000000000"
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BS(response.content, 'html.parser')
        return soup.find_all('tr', class_=['records_list_x', 'records_list_y'])
    except Exception as e:
        logging.error(f"Error fetching rows from {server_base_url}: {e}")
        return []

def process_row(row, server_base_url):
    """Extract campaign and list ID if conditions match."""
    td = row.find_all('td')
    if len(td) > 9:
        try:
            if (
                td[4].find('font') and td[4].find('font').text.strip() == 'LISTS' and
                td[8].find('font') and td[8].find('font').text.strip() == 'ADMIN ADD LIST'
            ):
                date_str = td[1].find('font').text.strip()
                row_time = est.localize(datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S'))
                if row_time >= thirty_minutes_ago:
                    href = td[9].find('a')['href']
                    list_url = f"{server_base_url}{href}"
                    return fetch_list_details(list_url)
        except Exception as e:
            logging.error(f"Error processing row: {e}")
    return None, None

def fetch_list_details(list_url):
    """Fetch campaign and list ID details."""
    try:
        response = requests.get(list_url)
        response.raise_for_status()
        soup = BS(response.content, 'html.parser')
        campaign = soup.find('select', attrs={'name': 'campaign_id'}).find('option', selected=True).text.strip()
        list_id = soup.find('tr', attrs={'bgcolor': '#B6D3FC'}).find('b').text.strip()
        return campaign, list_id
    except Exception as e:
        logging.error(f"Error fetching list details from {list_url}: {e}")
        return None, None

def send_slack_notification(channel, campaign, list_id):
    """Send a notification message to Slack."""
    message = f"<@{BOLAJI}> <@{ALEJANDRO}>, a new list has been added.\nList ID: {list_id}.\nCampaign: {campaign}"
    headers = {"Authorization": f"Bearer {SLACK_BOT}", "Content-Type": "application/json"}
    data = {"channel": channel, "text": message}
    try:
        response = requests.post("https://slack.com/api/chat.postMessage", headers=headers, json=data)
        response.raise_for_status()
        logging.info(f"Message sent to channel {channel}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to send Slack notification: {e}")

# Main Function
def main():
    for server in SERVERS:
        logging.info(f"Processing server: {server['name']}")
        rows = fetch_rows(server['base_url'])
        for row in rows:
            campaign, list_id = process_row(row, server['base_url'])
            if campaign and list_id:
                channel = server.get('channel_mapper', {}).get(campaign, server.get('channel'))
                if channel:
                    send_slack_notification(channel, campaign, list_id)

if __name__ == "__main__":
    main()
