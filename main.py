import requests
from bs4 import BeautifulSoup as BS
from datetime import datetime, timedelta
import pytz
from os import getenv
from dotenv import load_dotenv

load_dotenv()

user = getenv('SERVER_USER')
passwd = getenv('SERVER_PASS')

# Set the timezone to EST
est = pytz.timezone('US/Eastern')

# Calculate 30 minutes ago in EST
now = datetime.now(est)
thirty_minutes_ago = now - timedelta(minutes=30)

url = f"https://{user}:{passwd}@login.theccdocs.com/vicidial/admin.php?ADD=700000000000000"

re = requests.get(url)

soup = BS(re.content, 'html.parser')

rows = soup.find_all('tr', class_=['records_list_x', 'records_list_y'])


# count = 0


# Print each row's content where:
# - the 5th td value (nested in font) is "LISTS"
# - the 9th td value (nested in font) is "ADMIN ADD LIST"
# - the 2nd td date is within the last 30 minutes

for row in rows:
    # if count == 10:
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
                print("Href:", href)
            # count+=1