# PTT Article Reminder

## Supported services

- Line
- Telegram

## Prerequisie

### Python

- python>=3.7 (Tested 3.7/3.8)
- requests
- requests-html
- optional
    - line-bot-sdk==1.15.0 (If you want using line.)
    - python-telegram-bot (If you want using telegram.)

### Installation

    git clone https://github.com/qqaatw/PttArticleReminder --recursive

### Configuration file

**Should first create config.json in the folder.**

    {
    "services":
        [
            { // First used service.
                "name": "line",
                "enable": "true",
                "channel_access_token": "CHANNEL ACCESS TOKEN",
                "client_list": {
                    "custom name A": "USER ID TOKEN",
                    "custom name B": "USER ID TOKEN"
                }
                
            },
            { // Second used service, it will takeover when the first service failed.
                "name": "telegram",
                "enable": "false",
                "bot_token": "BOT TOKEN",
                "client_list": {
                    "custom name A": "CHAT ID OR USERNAME",
                    "custom name B": "CHAT ID OR USERNAME"
                }
            }
        ] 
    }

Note:

1. You can swap the order of each service.

## Usage

    python article_reminder.py \
        -b [board name] \
        -k [keywords, divided by comma] \
        -u [custom name in config.json]
    
    E.g. python article_reminder.py -b PC_Shopping -k cyberpower -b Storage_Zone -k toshiba,wd -u ABC
    
Notes:

1. There is a 30 mins watchdog timer in the loop to ensure that the program works fine.
2. Keywords are not case-sensitive.
3. You should add the bot as friend and start the chat with some messages before running PTT Article Reminder.

## License

- Apache 2.0
- Submodules:
    - CrawlerTutorial 由leVirve製作，以創用CC 姓名標示 4.0 國際 授權條款釋出。
