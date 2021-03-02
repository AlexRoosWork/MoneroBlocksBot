# MoneroBlocksBot

MoneroBlocksBot is a Telegram Bot, which uses the MoneroBlocks.info/api to give the user information about the Monero Blockchain and network. 

The Bot I host can be reached under @MoneroBlocksBot. Feel free to add it to your group.


## Requirements
* requests
* python-telegram-bot


## Supported Commands
* **/overview** - returns an overview of all stats
* **/height** - returns the current blockheight
* **/hashrate** - returns the current network hashrate in MH/s
* **/supply** - returns the total emission of all XMR
* **/last_reward** - returns the block reward of the latest block
* **/last_block** - returns the timestamp of latest block in UTC time
* **/tx_num** - returns the number of transactions in the latest block
* **/help** - gives the user an overview of all commands
* **/menu** - gives a button menu for user to click on


## New Feature Ideas
* **/inflation** -returns the annual inflation rate 
* **/tx_num BLOCKHEIGHT** - return the number of transactions in a specific block


## Recent Updates
* Added a button menu **/menu** for easier access
* Removed **/seconds_since** as a separate function and added it to **/last_block**
* Added the command **/overview** to view all stats in one message
* Added the command **/tx_num** to view the number of transactions in the latest block


## Credits
Feel free to fork and provide me with feedback and ideas. A big thanks to moneroblocks.info for the easy to use API, really makes programming this a joy. 

I don't believe in copyright.