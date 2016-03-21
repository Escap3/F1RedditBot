import praw #https://github.com/praw-dev/praw
import pdb, re, os, time
from config import *
from seasonsdict import dict
from results import *
from commentformatter import *

"""
Reddit bot that replies with results from formula 1 seasons / races
"""

"""
TODO:
* Implement something that checks spelling / country name etc
* Reply later function if the maximum number of calls to API has been made
* Other forms of results, constructors etc
"""

class F1Bot:

    r = praw.Reddit(AGENT)
    replied_to = []
    subreddit = r.get_subreddit(SUBREDDIT)
    requests = 0
    starttime = time.time()

    def __init__(self):
        self.r.login(USERNAME, PASSWORD)
        self.get_replied_to()


    def get_replied_to(self):
        if not os.path.isfile('replied_to.txt'):
            self.replied_to = []
        else:
            with open('replied_to.txt') as f:
                replies = f.read()
                self.replied_to = replies.split('\n')


    def run_bot(self):    

        """
        The main function of the bot. Will fetch 50 newest comments and
        check if they contain a string matching [[(.*)]]. If we find
        one and we are allowed to make more requests we create a comment
        and post it. Then save the id of the comment we replied to so we don't
        reply several times.
        """

        for comments in self.r.get_comments(SUBREDDIT, limit=50):
            if(re.search("\[\[(.*)\]\]", comments.body, re.IGNORECASE)):
                race = self.parse_comment(comments.body)     
                raceresult = None           
                if race[0] is not None:
                    if(allow_request()):  
                        self.requests += 1
                        raceresult = make_comment(race[0], race[1])
                if comments.id not in self.replied_to and raceresult is not None:
                    self.post_comment(comments, raceresult)
                    self.replied_to.append(comments.id)
                    print("Replied to:" + comments.id)
        with open('replied_to.txt', 'w') as f:
            for post in self.replied_to:
                f.write(post + '\n')


    def allow_request(self):

        """
        We are only allowed 200 requests per hour so this function
        makes sure we keep below that. If an hour has passed the
        time and requests made are reset.
        @return True if we are allowed to make a request
        """

        if (starttime + 3600 < time.time()):
            self.requests = 0
            self.starttime = time.time()
        return self.requests < 200


    def make_comment(self, race, year):

        """ 
        Creates the comment by getting the JSON from the Ergast API 
        (get_season_result) and sending the data to be parsed (convert_x_to_post)
        into a comment.
        @return The finished comment as a string or None if something went wrong
        """

        if(race == 'season'):
            result = get_season_result(year)
            raceresult = convert_season_to_post(result)                       
        else:
            result = get_race_result(year, race)
            raceresult = convert_race_to_post(result)
        return raceresult


    def parse_comment(self, text):

        """
        If a matching string has been found this function will split up the
        comment into parts. If it's a race it will try to find the 
        roundnumber. If we want a season we just return that.
        @return Tuple ['season' or the number of the race if found otherwise None, year]
        """

        str = re.search("\[\[(.*)\]\]", text, re.IGNORECASE)
        args = str.group(1).strip('.[]').replace(',','').split(' ')
        year = args.pop()
        circuit = args[0]
        if(circuit.lower() == 'season'):
            return ['season', year]
        roundnumber = self.find_roundnumber(circuit, year)
        return [roundnumber, year]


    def find_roundnumber(self, circuit, year):

        """
        Tries to find the round number for the requested GP.
        @return Round number if found otherwise None
        """

        if circuit in dict.get(year):
            return dict.get(year).index(circuit) + 1
        else:
            return None

    def post_comment(self, comment, result):
        comment.reply(result)
        

def check_config():
    if not os.path.isfile('config.py'):
        print("No config found, exiting...")
        exit(1)

if __name__ == "__main__":
    check_config()
    bot = F1Bot()
    while True:
        bot.run_bot()
        time.sleep(30)
