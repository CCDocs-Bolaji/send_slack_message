import logging
import requests
from bs4 import BeautifulSoup as BS
from datetime import datetime, timedelta
import pytz
from config import (
    USER, PASS, SLACK_CHANNELS, BOLAJI, ALEJANDRO, SLACK_BOT, 
    ROOFCON_USER, ROOFCON_PASS, CORNERSTONE_SLACK_CHANNEL
)
import time

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

def fetch_and_process_rows(server_name, server_base_url):
    """Fetch and process rows in a single function."""
    logging.info(f"Fetching rows from {server_name}...")
    url = f"{server_base_url}/vicidial/admin.php?ADD=700000000000000"
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BS(response.content, 'html.parser')
        rows = soup.find_all('tr', class_=['records_list_x', 'records_list_y'])
        valid_rows = []

        for row in rows:
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
                            logging.info(f"New list added in the last 30 minutes, fetching list details from {list_url}...")

                            # Fetch list details
                            response = requests.get(list_url)
                            response.raise_for_status()
                            soup = BS(response.content, 'html.parser')
                            campaign = soup.find('select', attrs={'name': 'campaign_id'}).find('option', selected=True).text.strip()
                            list_id = soup.find('tr', attrs={'bgcolor': '#B6D3FC'}).find('b').text.strip()
                            logging.info(f"List details fetched: Campaign = {campaign}, List ID = {list_id}")
                            valid_rows.append((campaign, list_id))

                except Exception as e:
                    logging.error(f"Error processing row: {e}")

        logging.info(f"Fetched {len(valid_rows)} valid rows successfully.")
        if not valid_rows:
            logging.info("No new lists added in the last 30 minutes.")
        return valid_rows

    except Exception as e:
        logging.error(f"Error fetching rows from {server_base_url}: {e}")
        return []


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
        valid_rows = fetch_and_process_rows(server['name'], server['base_url'])
        for campaign, list_id in valid_rows:
            channel = server.get('channel_mapper', {}).get(campaign, server.get('channel'))
            if channel:
                send_slack_notification(channel, campaign, list_id)
            time.sleep(10)  # Sleep to avoid overwhelming requests


if __name__ == "__main__":
    main()
