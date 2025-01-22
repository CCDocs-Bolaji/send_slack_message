import json
from os import getenv
from dotenv import load_dotenv

load_dotenv()

# NOTE : These variables are hardcoded on the CCDOCS server, there is no .env file

USER = getenv('CCDOCS_SERVER_USER')
PASS = getenv('CCDOCS_SERVER_PASS')

SLACK_CHANNELS = json.loads(getenv('CCDOCS_SLACK_CHANNELS', '{}'))

BOLAJI = getenv('BOLAJI')
ALEJANDRO = getenv('ALEJANDRO')
SLACK_BOT = getenv('SLACKBOT')