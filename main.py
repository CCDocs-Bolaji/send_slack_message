import logging
import requests
from bs4 import BeautifulSoup as BS
from datetime import datetime, timedelta
import pytz
from config import USER, PASS, SLACK_CHANNELS, BOLAJI, ALEJANDRO, SLACK_BOT, ROOFCON_USER, ROOFCON_PASS, CORNERSTONE_SLACK_CHANNEL

# CCDOCS SERVER CLIENTS

logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("list_alert.log"),
    ]
)

# Set the timezone to EST
est = pytz.timezone('US/Eastern')

# Calculate 30 minutes ago in EST
now = datetime.now(est)
thirty_minutes_ago = now - timedelta(minutes=30)
base_url = f'https://{USER}:{PASS}@login.theccdocs.com'
url = f"{base_url}/vicidial/admin.php?ADD=700000000000000"
response = requests.get(url)

if response.status_code != 200:
    logging.error(f"Failed to fetch the main page. Status Code: {response.status_code}")
    exit()

soup = BS(response.content, 'html.parser')

rows = soup.find_all('tr', class_=['records_list_x', 'records_list_y'])


# count = 0


# Print each row's content where:
# - the 5th td value (nested in font) is "LISTS"
# - the 9th td value (nested in font) is "ADMIN ADD LIST"
# - the 2nd td date is within the last 30 minutes

for row in rows:
    # if count == 1:
    #     break
    td = row.find_all('td')
    if len(td) > 9:
        font_5th_td = td[4].find('font')
        font_9th_td = td[8].find('font')
        link_10th_td = td[9].find('a')
        if (
            font_5th_td and font_5th_td.text.strip() == 'LISTS' and
            font_9th_td and font_9th_td.text.strip() == 'ADMIN ADD LIST'
        ):
            date_str = td[1].find('font').text.strip()
            # Parse the date and time
            row_time = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
            row_time = est.localize(row_time)
            if row_time >= thirty_minutes_ago:
                href = link_10th_td['href']
                list_url = f'{base_url}{href}'
                list_page = requests.get(list_url)
                if list_page.status_code == 200:
                    new_soup = BS(list_page.content, 'html.parser')
                    campaign = new_soup.find('select', attrs={'name': 'campaign_id'}).find('option', attrs={'selected': True}).text.strip()
                    list_id = new_soup.find('tr', attrs={'bgcolor': '#B6D3FC'}).find('b').text.strip()

                    channel_id = SLACK_CHANNELS.get(campaign, '')

                    message = f"<@{BOLAJI}> <@{ALEJANDRO}>, a new list added has been added in the dialer.\nList ID : {list_id}.\nCampaign : {campaign}"
                    url = "https://slack.com/api/chat.postMessage"
                    headers = {"Authorization": f"Bearer {SLACK_BOT}", "Content-Type": "application/json"}
                    data = {"channel": channel_id, "text": message}
                    try:
                        response = requests.post(url, headers=headers, json=data)
                        response.raise_for_status()
                        logging.info(f"Success: message sent to {campaign}'s slack channel")
                    except requests.exceptions.RequestException as e:
                        logging.error(f"Error sending message to Slack: {e}")
                else:
                    logging.error(f"Failed to fetch list details. Status Code: {list_page.status_code}")
            # count+=1


# CORNERSTONE SERVER
base_url = f'https://{ROOFCON_USER}:{ROOFCON_PASS}@cornerconstruction.ccdocs.com'
url = f"{base_url}/vicidial/admin.php?ADD=700000000000000"
response = requests.get(url)

if response.status_code != 200:
    logging.error(f"Failed to fetch the main page. Status Code: {response.status_code}")
    exit()

soup = BS(response.content, 'html.parser')

rows = soup.find_all('tr', class_=['records_list_x', 'records_list_y'])


# count = 0


# Print each row's content where:
# - the 5th td value (nested in font) is "LISTS"
# - the 9th td value (nested in font) is "ADMIN ADD LIST"
# - the 2nd td date is within the last 30 minutes

for row in rows:
    # if count == 1:
    #     break
    td = row.find_all('td')
    if len(td) > 9:
        font_5th_td = td[4].find('font')
        font_9th_td = td[8].find('font')
        link_10th_td = td[9].find('a')
        if (
            font_5th_td and font_5th_td.text.strip() == 'LISTS' and
            font_9th_td and font_9th_td.text.strip() == 'ADMIN ADD LIST'
        ):
            date_str = td[1].find('font').text.strip()
            # Parse the date and time
            row_time = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
            row_time = est.localize(row_time)
            if row_time >= thirty_minutes_ago:
                href = link_10th_td['href']
                list_url = f'{base_url}{href}'
                list_page = requests.get(list_url)
                if list_page.status_code == 200:
                    new_soup = BS(list_page.content, 'html.parser')
                    campaign = new_soup.find('select', attrs={'name': 'campaign_id'}).find('option', attrs={'selected': True}).text.strip()
                    list_id = new_soup.find('tr', attrs={'bgcolor': '#B6D3FC'}).find('b').text.strip()

                    channel_id = CORNERSTONE_SLACK_CHANNEL

                    message = f"<@{BOLAJI}> <@{ALEJANDRO}>, a new list added has been added in the dialer.\nList ID : {list_id}.\nCampaign : {campaign} IGNORE THIS IS FOR TESTING PURPOSES"
                    url = "https://slack.com/api/chat.postMessage"
                    headers = {"Authorization": f"Bearer {SLACK_BOT}", "Content-Type": "application/json"}
                    data = {"channel": channel_id, "text": message}
                    try:
                        response = requests.post(url, headers=headers, json=data)
                        response.raise_for_status()
                        logging.info(f"Success: message sent to {campaign}'s slack channel")
                    except requests.exceptions.RequestException as e:
                        logging.error(f"Error sending message to Slack: {e}")
                else:
                    logging.error(f"Failed to fetch list details. Status Code: {list_page.status_code}")
            # count+=1