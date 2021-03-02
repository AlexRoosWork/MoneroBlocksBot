"""
TelegramBot that tells users some stats about the Monero Network. Using the MoneroBlock.info API and Python Telegram TelegramBot
"""

"""
Using the API of MoneroBlocks.info, we get information about the Monero Network
"""

import logging
import json
import requests
import datetime
import time
import sys, os

from telegram import ParseMode, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler


# BASIC CONFIGURATIONS

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

logger = logging.getLogger(__name__)

# basedir of the python script - in that dir the token has to be placed
BASE_DIR = os.path.dirname(sys.argv[0])

# read token and store as variable
with open(BASE_DIR + os.sep + 'token') as token_file:
    token = token_file.read()

url_base = "http://moneroblocks.info/api/"  # url for making the API calls


# LOGIC OF THE MONERO BLOCKS API

def get_stats():
    """
    Construct the url to get the general stats. 
    
    Includes:
    * difficulty
    * height
    * hashrate
    * total_emission
    * last_reward
    * last_timestamp
    """
    url = url_base + "get_stats/"  # construct the url 
    json = make_request(url)
    return json


def make_request(url):
    """Make the request to MoneroBlocks. Return the json file"""
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
    except IOError as e:
        print(f"Connection error {e} with server")


def get_height():
    """Returns the current blockchain height"""
    json_file = get_stats()
    height = str(json_file['height'])
    html_string = f'The <b>current block height</b> is <code>{height}</code>'
    return html_string, height


def get_hashrate():
    """Returns network hashrate in mh/s"""
    json_file = get_stats()
    hashrate = (round(json_file['hashrate'] / 1_000_000, 3))
    html_string = f'The <b>current network hashrate</b> is approximately <code>{hashrate:,} MH/s</code>'
    return html_string


def get_coinsupply():
    """Get the total number of XMR in circulation"""
    json_file = get_stats()
    coinsupply = (int(json_file['total_emission']) // 1_000_000_000_000)
    html_string = f'The <b>total coinsupply</b> is <code>{coinsupply:,} XMR</code>'
    return html_string


def get_last_reward():
    """Get the reward of the last block"""
    json_file = get_stats()
    last_reward = (round(int(json_file['last_reward']) / 1_000_000_000_000, 4))
    html_string = f'The <b>last block reward</b> was approximately <code>{last_reward:,} XMR</code>'
    return html_string


def get_last_block_time():
    """Get unix time and convert it into a human readable string
    Format: dd/MM/YYYY HH:mm:ss"""
    json_file = get_stats()
    unix_time = json_file['last_timestamp']
    last_block_time = datetime.datetime.utcfromtimestamp(unix_time).strftime('%d %b %Y %H:%M:%S')
    timedelta_last_block = round(time.time() - unix_time, 2)
    html_string = f'The <b>last block</b> was found at <code>{last_block_time} UTC ({timedelta_last_block} secs ago)</code> '
    return html_string


def get_transaction_num():
    """Get the number of transactions from the last block"""
    _, last_block_height = get_height()  # get blockheight from existing function

    # make new request with the recent blockheight and get block details
    api_url = 'http://moneroblocks.info/api/get_block_header/'
    json_file = make_request(api_url + str(last_block_height))
    tx_num = json_file['block_header']['num_txes']

    # some fancy gramatic
    if tx_num == 1:
        html_string = f'The <b>last block</b> <code>#{last_block_height}</code> had <code>{tx_num}</code> <b>transaction</b> in it.'
    else:
        html_string = f'The <b>last block</b> <code>#{last_block_height}</code> had <code>{tx_num}</code> <b>transactions</b> in it.'

    return html_string, tx_num


def get_overview():
    """Get an overview of the monero network"""
    json_file = get_stats()
    height = json_file['height']
    hashrate = json_file['hashrate']
    supply = json_file['total_emission']
    reward = json_file['last_reward']
    last_timestamp = json_file['last_timestamp']
    seconds_since = round(time.time() - last_timestamp, 2)
    _, tx_num = get_transaction_num()
    formatted_utc_time = datetime.datetime.utcfromtimestamp(last_timestamp).strftime('%d %b %Y %H:%M:%S')

    # format the string
    overview_1 = f'<b>Current blockheight</b>: \t<code>{height}</code>\n<b>Network Hashrate</b>: \t<code>{round(hashrate / 1_000_000, 3)} MH/s</code>'
    overview_2 = f'\n<b>Total Supply</b>: \t<code>{int(supply) // 1_000_000_000_000} XMR</code>\n<b>Last Reward</b>: \t<code>{round(int(reward) / 1_000_000_000_000, 4)} XMR</code>'
    overview_3 = f'\n<b>Last block found</b>: \t<code>{formatted_utc_time} UTC</code>\t<code>({seconds_since} secs ago)</code> included <code>{tx_num}</code> TX'

    html_string = overview_1 + overview_2 + overview_3
    return html_string


def get_help():
    """Format the help string"""
    string_start = 'MoneroBlocksBot gives you stats about the Monero Blockchain and network.\n'
    string_overview = '\n<b>Commands are:</b>\n\n<code>/menu</code> shows a button menu\n<code>/overview</code> for all stats in one message'
    string_commands = "\n<code>/height</code> for the current block height\n<code>/supply</code> for the total coinsupply\n<code>/reward</code> for the last block reward\n<code>/hashrate</code> for current network hashrate\n<code>/last_block</code> for the timestamp of the latest block\n"
    string_end = "<code>/tx_num</code> for the number of transactions in the latest block\n\nA big thanks goes to MoneroBlocks.info for their awesome API."

    html_string = string_start + string_overview + string_commands + string_end
    return html_string


# LOGIC FOR THE TELEGRAM BOT
def display_height(update, context):
    """Output the blockchain height in formatted html text"""
    html_string, _ = get_height()
    update.message.reply_html(html_string)


def display_hashrate(update, context):
    """Output the network hashrate in formatted html text"""
    html_string = get_hashrate()
    update.message.reply_html(html_string)


def display_coinsupply(update, context):
    """Output the total emission in formatted html text"""
    html_string = get_coinsupply()
    update.message.reply_html(html_string)


def display_last_reward(update, context):
    """Output the last reward in XMR in formatted html text"""
    html_string = get_last_reward()
    update.message.reply_html(html_string)


def display_last_block_time(update, context):
    """Output the timestamp of the last block in formatted html text"""
    html_string = get_last_block_time()
    update.message.reply_html(html_string)


def display_tx_num(update, context):
    """Output a formatted string with the number of transactions in the last block"""
    html_string, _ = get_transaction_num()
    update.message.reply_html(html_string)


def display_overview(update, context):
    """Output a formatted string with all stats"""
    # get the json file and store values in variables
    html_string = get_overview()
    update.message.reply_html(html_string)


def display_menu(update, context):
    """Display a button menu with all available commands"""
    keyboard = [
        [InlineKeyboardButton("Overview", callback_data='overview')], 
        [InlineKeyboardButton("Timestamp", callback_data='timestamp'),
        InlineKeyboardButton("Blockheight", callback_data='height')],
        [InlineKeyboardButton("Supply", callback_data='supply'), 
        InlineKeyboardButton("Reward", callback_data='reward')],
        [InlineKeyboardButton("Hashrate", callback_data='hashrate'), 
        InlineKeyboardButton("Transactions", callback_data='tx_num')],
        [InlineKeyboardButton("Help Message", callback_data='help')]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_html("<b><i>Explore the Monero Network</i></b>", reply_markup=reply_markup)


def menu_button(update, context):
    """Execute functions of the selected menu point"""
    query = update.callback_query
    if query.data == 'height':
        html_string, _ = get_height()
    elif query.data == 'supply':
        html_string = get_coinsupply()
    elif query.data == 'reward':
        html_string = get_last_reward()
    elif query.data == 'hashrate':
        html_string = get_hashrate()
    elif query.data == 'tx_num':
        html_string, _ = get_transaction_num()
    elif query.data == 'overview':
        html_string = get_overview()
    elif query.data == 'timestamp':
        html_string = get_last_block_time()
    elif query.data == 'help':
        html_string = get_help()
    
    # return the matching html string
    query.edit_message_text(text=html_string, parse_mode="HTML")


def help(update, context):
    """Display a help message"""
    html_string = get_help()
    update.message.reply_html(html_string)


def error(update, context):
    """Log warnings"""
    logging.warning(f"Update {update} caused error {context.error}")


def main():
    """Run the telegram bot with the commands"""
    updater = Updater(token, use_context=True)

    dp = updater.dispatcher

    # Commands
    dp.add_handler(CommandHandler("height", display_height))
    dp.add_handler(CommandHandler("hashrate", display_hashrate))
    dp.add_handler(CommandHandler("supply", display_coinsupply))
    dp.add_handler(CommandHandler("reward", display_last_reward))
    dp.add_handler(CommandHandler("last_block", display_last_block_time))
    dp.add_handler(CommandHandler("tx_num", display_tx_num))
    dp.add_handler(CommandHandler("overview", display_overview))
    dp.add_handler(CommandHandler("menu", display_menu))
    dp.add_handler(CallbackQueryHandler(menu_button))
    dp.add_handler(CommandHandler("help", help))

    # Error
    dp.add_error_handler(error)

    # Start Bot and run
    updater.start_polling()

    updater.idle()

if __name__ == "__main__":
    main()

