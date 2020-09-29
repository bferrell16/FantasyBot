import requests
import json
import os
import random
from apscheduler.schedulers.blocking import BlockingScheduler
from espn_api.football import League

class GroupMeException(Exception):
    pass

class GroupMeBot(object):
    #Creates GroupMe Bot to send messages
    def __init__(self, bot_id):
        self.bot_id = bot_id

    def __repr__(self):
        return "GroupMeBot(%s)" % self.bot_id

    def send_message(self, text):
        #Sends a message to the chatroom
        template = {
                    "bot_id": self.bot_id,
                    "text": text,
                    "attachments": []
                    }

        headers = {'content-type': 'application/json'}

        if self.bot_id not in (1, "1", ''):
            r = requests.post("https://api.groupme.com/v3/bots/post",
                              data=json.dumps(template), headers=headers)
            if r.status_code != 202:
                raise GroupMeException('Invalid BOT_ID')

            return r

    def send_message_with_picture(self, text, picture=None):
        #Sends a message to the chatroom
        template = {
                    "bot_id": self.bot_id,
                    "text": text,
                    'picture_url':picture,
                    "attachments": []
                    }

        headers = {'content-type': 'application/json'}

        if self.bot_id not in (1, "1", ''):
            r = requests.post("https://api.groupme.com/v3/bots/post",
                              data=json.dumps(template), headers=headers)
            if r.status_code != 202:
                raise GroupMeException('Invalid BOT_ID')

            return r

def get_scoreboard_short(league, week=None):
    #Gets current week's scoreboard
    box_scores = league.box_scores(week=week)
    score = ['%s %.2f - %.2f %s' % (i.home_team.team_abbrev, i.home_score,
             i.away_score, i.away_team.team_abbrev) for i in box_scores
             if i.away_team]
    text = ['Score Update'] + score
    return '\n'.join(text)

def all_played(lineup):
    for i in lineup:
        if i.slot_position != 'BE' and i.game_played < 100:
            return False
    return True


def get_power_rankings(league, week=None):
    # power rankings requires an integer value, so this grabs the current week for that
    if not week:
        week = league.current_week
    #Gets current week's power rankings
    #Using 2 step dominance, as well as a combination of points scored and margin of victory.
    #It's weighted 80/15/5 respectively
    power_rankings = league.power_rankings(week=week)

    score = ['%s - %s' % (i[0], i[1].team_name) for i in power_rankings if i]
    text = ['Power Rankings'] + score
    return '\n'.join(text)

def he_who_sucks_the_most(league, week=None):
    if not week:
        week = league.current_week
    power_rankings = league.power_rankings(week=week)
    pic = ""
    if power_rankings[9][1].team_name == 'The EBITDAddys':
        pic = "https://i.imgur.com/YIjpIaD.jpg"
    elif power_rankings[9][1].team_name == 'Tua Bortions':
        pic = 'https://i.imgur.com/Xrxfq07.jpg'
    elif power_rankings[9][1].team_name == 'College Park Party Poopers':
        pic = 'https://i.imgur.com/EnNldNg.jpg'
    elif power_rankings[9][1].team_name == 'Mona HandJobs':
        pic = 'https://i.imgur.com/gjCXYIS.jpg'
    elif power_rankings[9][1].team_name == 'Team Pfarr':
        pic = 'https://i.imgur.com/zlWWE6L.jpg'
    elif power_rankings[9][1].team_name == 'D.C. Defenders':
        pic = 'https://i.imgur.com/dIRLZb4.jpg'
    elif power_rankings[9][1].team_name == 'Mr. Larceny':
        pic = 'https://i.imgur.com/tqKpSKo.jpg'
    elif power_rankings[9][1].team_name == 'All Mahomies Hate Football':
        pic = 'https://i.imgur.com/zlWWE6L.jpg'
    elif power_rankings[9][1].team_name == 'Team Whitney':
        pic = 'https://i.imgur.com/XkcljmK.jpg'
    elif power_rankings[9][1].team_name == 'Supreme Lord Marty':
        pic = 'https://i.imgur.com/pX79oCQ.jpg'
    return pic

def get_trophies(league, week=None):
    #Gets trophies for highest score, lowest score, closest score, and biggest win
    matchups = league.box_scores(week=week)
    low_score = 9999
    low_team_name = ''
    high_score = -1
    high_team_name = ''
    closest_score = 9999
    close_winner = ''
    close_loser = ''
    biggest_blowout = -1
    blown_out_team_name = ''
    ownerer_team_name = ''

    for i in matchups:
        if i.home_score > high_score:
            high_score = i.home_score
            high_team_name = i.home_team.team_name
        if i.home_score < low_score:
            low_score = i.home_score
            low_team_name = i.home_team.team_name
        if i.away_score > high_score:
            high_score = i.away_score
            high_team_name = i.away_team.team_name
        if i.away_score < low_score:
            low_score = i.away_score
            low_team_name = i.away_team.team_name
        if i.away_score - i.home_score != 0 and \
            abs(i.away_score - i.home_score) < closest_score:
            closest_score = abs(i.away_score - i.home_score)
            if i.away_score - i.home_score < 0:
                close_winner = i.home_team.team_name
                close_loser = i.away_team.team_name
            else:
                close_winner = i.away_team.team_name
                close_loser = i.home_team.team_name
        if abs(i.away_score - i.home_score) > biggest_blowout:
            biggest_blowout = abs(i.away_score - i.home_score)
            if i.away_score - i.home_score < 0:
                ownerer_team_name = i.home_team.team_name
                blown_out_team_name = i.away_team.team_name
            else:
                ownerer_team_name = i.away_team.team_name
                blown_out_team_name = i.home_team.team_name

    low_score_str = ['Low score: %s with %.2f points' % (low_team_name, low_score)]
    high_score_str = ['High score: %s with %.2f points' % (high_team_name, high_score)]
    close_score_str = ['%s barely beat %s by a margin of %.2f' % (close_winner, close_loser, closest_score)]
    blowout_str = ['%s blown out by %s by a margin of %.2f' % (blown_out_team_name, ownerer_team_name, biggest_blowout)]

    text = ['Trophies of the week:'] + low_score_str + high_score_str + close_score_str + blowout_str
    return '\n'.join(text)

def bot_main(function):
    try:
        bot_id = 'e9042ce779195e8b2e2685691c' #e9042ce779195e8b2e2685691c
    except KeyError:
        bot_id = 1

    league_id = 18765232
    league_idB = 94443769

    try:
        year = int(os.environ["LEAGUE_YEAR"])
    except KeyError:
        year=2020

    try:
        swid = os.environ["SWID"]
    except KeyError:
        swid='{1}'

    if swid.find("{",0) == -1:
        swid = "{" + swid
    if swid.find("}",-1) == -1:
        swid = swid + "}"

    try:
        espn_s2 = os.environ["ESPN_S2"]
    except KeyError:
        espn_s2 = '1'

    try:
        espn_username = os.environ["ESPN_USERNAME"]
    except KeyError:
        espn_username = '1'

    try:
        espn_password = os.environ["ESPN_PASSWORD"]
    except KeyError:
        espn_password = '1'

    bot = GroupMeBot(bot_id)

    if swid == '{1}' and espn_s2 == '1': # and espn_username == '1' and espn_password == '1':
        league = League(league_id=league_id, year=year)
        league2 = League(league_id=league_idB, year=year)
#    if espn_username and espn_password:
#        league = League(league_id=league_id, year=year, username=espn_username, password=espn_password)

    text = ''

    test = False
    if test:
        week = league.current_week - 1
        sucks = he_who_sucks_the_most(league2, week=week)
        bot.send_message_with_picture('', sucks)


    if function=="get_scoreboard_short":
        text = get_scoreboard_short(league)
    elif function=="get_power_rankings":
        text = text + "League A \n"
        text = text + get_power_rankings(league)       
        text = text + "\nLeague B \n"
        text = text + get_power_rankings(league2)   
    elif function=="get_trophies": #should be able to remove this?
        text = get_trophies(league)
    elif function=="get_final":
        # on Tuesday we need to get the scores of last week
        week = league.current_week - 1
        text = "League A \n"
        text = text +"Final " + get_scoreboard_short(league, week=week)
        text = text + "\n" + get_trophies(league, week=week)
        text = text + "\n\nLeague B \n"
        text = text + "Final " + get_scoreboard_short(league2, week=week)
        text = text + "\n" + get_trophies(league2, week=week)
    elif function=="worst_team":
        week = league.current_week - 1
        sucks = he_who_sucks_the_most(league2, week=week)
        bot.send_message_with_picture('', sucks)
    elif function=="init":
        try:
            text = ''
        except KeyError:
            #do nothing here, empty init message
            pass
    else:
        text = "Something happened. HALP"

    if text != '' and not test and function!="init" and function != "worst_team":
        bot.send_message(text)

    if test:
        #print "get_final" function
        print(text)


if __name__ == '__main__':
    try:
        ff_start_date = os.environ["START_DATE"]
    except KeyError:
        ff_start_date='2020-09-04'

    try:
        ff_end_date = os.environ["END_DATE"]
    except KeyError:
        ff_end_date='2020-12-30'

    try:
        my_timezone = os.environ["TIMEZONE"]
    except KeyError:
        my_timezone='America/New_York'

    game_timezone='America/New_York'
    bot_main("init")
    sched = BlockingScheduler(job_defaults={'misfire_grace_time': 15*60})

    #power rankings:                     tuesday evening at 6:30pm local time.
    #worst player SVP picture            tuesday evening at 6:31pm local time.
    #trophies:                           tuesday morning at 7:30am local time.

    sched.add_job(bot_main, 'cron', ['get_power_rankings'], id='power_rankings',
        day_of_week='tue', hour=18, minute=0, start_date=ff_start_date, end_date=ff_end_date,
        timezone=my_timezone, replace_existing=True)
    sched.add_job(bot_main, 'cron', ['worst_team'], id='worst_team',
        day_of_week='tue', hour=18, minute=1, start_date=ff_start_date, end_date=ff_end_date,
        timezone=my_timezone, replace_existing=True)
    sched.add_job(bot_main, 'cron', ['get_final'], id='final',
        day_of_week='tue', hour=7, minute=30, start_date=ff_start_date, end_date=ff_end_date,
        timezone=my_timezone, replace_existing=True)

    print("Ready!")
    sched.start()
