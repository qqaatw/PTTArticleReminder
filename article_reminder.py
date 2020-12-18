import argparse
import asyncio
import re
import sys
import traceback

sys.path.insert(0, 'CrawlerTutorial/ptt-parser/')
import ptt

import api_handler


class ArticleReminder:
    """Periodically checking new articles on ptt.
    
    Parameters
    ----------
    num_meta : int, optional
        Metas to be fetched, by default 15.
    watchdog_interval: int, optional (minute)
        Interval of watchdog timer, by default 30. 
    """

    def __init__(self, num_meta=15, watchdog_interval=30):
        self.num_meta = num_meta  # Amount of article to fetch
        self.watchdog_interval = watchdog_interval
        self.current_file_id = {}  # Recording the newest article file id
    
    async def run(self, keywords, boards, receiver):
        """Run loop.

        Parameters
        ----------
        keywords : list of str
            Keywords to be fetched.
        boards : list of str
            Boards to be fetched.
        receiver : list of str
            Notification receiver, should be the key of client_list, by default None.
        """

        tasks = []
        loop = asyncio.get_running_loop()

        for i, board in enumerate(boards):
            tasks.append(self._loop(keywords[i].split(',') , board, receiver))
        try:
            await asyncio.gather(*tasks, return_exceptions=True)
        except asyncio.CancelledError as e:
            api_handler.send_message('Service terminated.', receiver)
        except:
            traceback.print_exc()
        finally:
            loop.stop()

    async def _loop(self, keyword, board_name, receiver=None):
        """Asynchronously fetch ptt matas and check required information.
        
        Parameters
        ----------
        keyword : str or list of str
            Keywords you want to detect and fetch.
        board_name : str
            Ptt board name.
        receiver : str, optional
            Notification receiver, should be the key of client_list, by default None. 
        """

        if board_name not in self.current_file_id:
            self.current_file_id[board_name] = 0
        if not isinstance(keyword, list):
            keyword = [keyword]

        # Start reminder
        print('Start:')
        if receiver:
            api_handler.send_message('Service start, searching in {}, for keywords:{}.'.format(board_name, keyword), receiver)
        else:
            api_handler.broadcast_message('Service start, searching in {}, for keywords:{}.'.format(board_name, keyword))
        print('Test:')
        self.pttGetMetadata('', board_name)

        watchdog = 0  # minute

        while True:
            if watchdog < self.watchdog_interval:
                watchdog +=1
            else:
                watchdog = 0
                api_handler.send_message('Watchdog: {}'.format(board_name), receiver)

            try:
                result = self.pttGetMetadata(keyword, board_name)
            except:
                traceback.print_exc()

            for r in result:
                api_handler.send_message('New article \n {}'.format(r), receiver)
            await asyncio.sleep(60)
            

    def pttGetMetadata(self, keyword, board_name):
        board = ptt.Board(board_name)
        meta = board.get_meta(num=self.num_meta)
        new_file_id = []
        founds = []

        assert len(meta) == self.num_meta

        for m in meta:
            if re.search(self.filter_string('|'.join(map(re.escape, keyword))), self.filter_string(m.title)) and m.author != '-':
                ptt_file_id = int(re.findall('\d+', m.filename)[0])

                # Try to get the latest articles.
                # Marked and locked articles are filtered out.
                if ptt_file_id > self.current_file_id[board_name] and \
                    m.mark != 'M' and \
                    m.mark != '!':
                    new_file_id.append(ptt_file_id)
                    founds.append(
                        'Board: {0} \n Date: {1} \n Author: {2} \n Title: {3} \n Link: https://www.ptt.cc{4}'.format(
                            board_name, 
                            m.date, 
                            m.author, 
                            m.title, 
                            m.link))
                    print("{} {}".format(m.date, m.title))
        if len(new_file_id) > 0:
            self.current_file_id[board_name] = max(new_file_id)
        return founds
    
    def filter_string(self, string):
        """
            Filter spaces and lowercase string.
        """

        return re.sub(' +', '', string).lower()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    
    parser.add_argument("-b", "--boards", help="Ptt boards to be fetched,",
                            type=str, action='append')
    parser.add_argument("-k", "--keywords", help="Keywords to be fetched. For multiple keywords, divided it by commas.",
                            type=str, action='append')
    parser.add_argument("-u", "--username", help="Username to send the notifications.",
                            type=str, default=None)
    parser.add_argument("-w", "--watchdog", help="Set watchdog timer in minute. By default 30 minutes.",
                            type=int, default=30)
    args = parser.parse_args()
    
    
    reminder = ArticleReminder(watchdog_interval=args.watchdog)
    
    asyncio.run(reminder.run(args.keywords, args.boards, args.username))