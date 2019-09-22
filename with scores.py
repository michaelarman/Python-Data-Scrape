import re
import requests
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
from urllib.request import urlopen as uReq
import csv
from collections import defaultdict
#import pprint
import csv

def get_links():
    print("getting links...")
    teams = ['algoma', 'brock', 'carleton', 'guelph', 'lakehead', 'laurentian',
             'laurier', 'mcmaster', 'nipissing', 'ottawa', 'queens', 'ryerson',
             'toronto', 'waterloo', 'western', 'windsor', 'york']
    years = ['2014-15', '2015-16', '2016-17', '2017-18', '2018-19']
    original_url = 'http://oua.ca/sports/mbkb/'
    end_url = '?view=gamelog'
    href_list = []
    for year in years:
        for team in teams:
            current_url = original_url + year + '/teams/' + team + end_url
            r = requests.get(current_url)
            raw_html = r.content
            soup = BeautifulSoup(raw_html, 'html.parser')
            tables = soup.findAll('table')
            max_len = 0
            index = 0

            for i in range(len(tables)):
                tags = tables[i].findAll('a')
                if len(tags) > 0:
                    url = tags[0].get('href', None)
                    if "/boxscores/20" in url and len(tables[i]) > max_len:
                        index = i
                        max_len = len(tables[i])

            table = tables[index]

            tags = table.findAll('a')
            for tag in tags:
                url = re.sub("\.\.", original_url + year, tag.get('href', None))
                url += '?view=teamstats'
                href_list.append(url)

    print("done getting links")
    return href_list


def scrape(url):
    """ This function is used to create data dictionaries for any url of team stats in the oua website. It
    takes an array of urls but for some games there are extra fields to look out for. This function is for those that
    do not have those extra fields in the table"""

    # create dictionary for links with less fields in table
    dictlist = {}
    for i in range(len(url)):

        print(url[i])
        r = requests.get(url[i])
        raw_html = r.content
        soup = BeautifulSoup(raw_html, 'html.parser')
        soup[url[i]] = BeautifulSoup(raw_html, 'html.parser')
        stats = soup[url[i]].findAll("table")
        scores = soup[url[i]].findAll('div', {'class': 'teams clearfix'})[0].table
        #winner = scores.findAll('tr',{'class' : 'winner'})[0]
        #loser = scores.findAll('tr',{'class' : 'loser'})[0]
        # some links have different amounts of tables and sometimes the team stats table is different
        table = stats[8]
        for j in range(2, len(stats)):
            if str(stats[j].caption) == '<caption class="caption offscreen"><h2>Team Statistics</h2></caption>':
                table=stats[j]
                break

        dictlist[url[i]] = {}
        d = {}

        dictlist[url[i]] = {
            "Away" : table.findAll('th', {'scope': 'col'})[1].text.strip(),
            "Home" : table.findAll('th', {'scope': 'col'})[2].text.strip(),
            #"Winner" : winner.th.text.strip(),
            # "Winner 1st Qtr Pts" : winner.findAll('td')[0].text.strip(),
            # "Winner 2nd Qtr Pts" : winner.findAll('td')[1].text.strip(),
            # "Winner 3rd Qtr" : winner.findAll('td')[2].text.strip(),
            # "Winner 4th Qtr" : winner.findAll('td')[3].text.strip(),
            # #"Winner Total Pts" : winner.findAll('td')[4].text.strip(),
            # #"Loser" : loser.th.text.strip(),
            # "Loser 1st Qtr Pts" : loser.findAll('td')[0].text.strip(),
            # "Loser 2nd Qtr Pts" : loser.findAll('td')[1].text.strip(),
            # "Loser 3rd Qtr Pts" : loser.findAll('td')[2].text.strip(),
            # "Loser 4th Qtr Pts" : loser.findAll('td')[3].text.strip(),
            #"Loser Total Pts" : loser.findAll('td')[4].text.strip()
        }
        try:
            winner = scores.findAll('tr', {'class': 'winner'})[0]
        except IndexError:
            d[None] = None
        try:
            loser = scores.findAll('tr', {'class': 'loser'})[0]
        except IndexError:
            d[None] = None
        try:
            dictlist[url[i]].update({"Winner": winner.th.text.strip()})
        except IndexError:
            d[None] = None
        try:
            dictlist[url[i]].update({"Loser": loser.th.text.strip()})
        except IndexError:
            d[None] = None
        # for k in range(1,6):
        #     dictlist[url[i]].update({"Winner Qtr" +k +Pts"})
        try:
            dictlist[url[i]].update({"Winner 1st Qtr Pts": winner.findAll('td')[0].text.strip()})
        except IndexError:
            d[None] = None
        try:
            dictlist[url[i]].update({"Loser 1st Qtr Pts": loser.findAll('td')[0].text.strip()})
        except IndexError:
            d[None] = None
        try:
            dictlist[url[i]].update({"Winner 2nd Qtr Pts": winner.findAll('td')[1].text.strip()})
        except IndexError:
            d[None] = None
        try:
            dictlist[url[i]].update({"Loser 2nd Qtr Pts": loser.findAll('td')[1].text.strip()})
        except IndexError:
            d[None] = None
        try:
            dictlist[url[i]].update({"Winner 3rd Qtr Pts": winner.findAll('td')[2].text.strip()})
        except IndexError:
            d[None] = None
        try:
            dictlist[url[i]].update({"Loser 3rd Qtr Pts": loser.findAll('td')[2].text.strip()})
        except IndexError:
            d[None] = None
        try:
            dictlist[url[i]].update({"Winner 4th Qtr Pts": winner.findAll('td')[3].text.strip()})
        except IndexError:
            d[None] = None
        try:
            dictlist[url[i]].update({"Loser 4th Qtr Pts": loser.findAll('td')[3].text.strip()})
        except IndexError:
            d[None] = None
        try:
            dictlist[url[i]].update( {"Winner Total Pts": winner.findAll('td')[4].text.strip()})
        except IndexError:
            d[None] = None
        try:
            dictlist[url[i]].update( {"Loser Total Pts": loser.findAll('td')[4].text.strip()})
        except IndexError:
            d[None] = None
        for j in range(16):
            try:
                dictlist[url[i]].update( { table.findAll('th', {'scope': 'row'})[j].text.strip() + ' Away': table.findAll('td')[2*j].text.strip()})
            except IndexError:
                d[None] = None
            try:
                dictlist[url[i]].update({ table.findAll('th', {'scope': 'row'})[j].text.strip() + ' Home' : table.findAll('td')[2*j+1].text.strip()})
            except IndexError:
                d[None] = None
            try:
                dictlist[url[i]].update({table.findAll('th', {'scope': 'row'})[16].text.strip()+' Away': table.findAll('td')[32].text.strip()})
            except IndexError:
                d[None] = None
    z = {**dictlist, **d}

    return z


if __name__ == '__main__':
    # q = ['http://oua.ca/sports/mbkb/2014-15/boxscores/20141107_ekyz.xml?view=teamstats','http://oua.ca/sports/mbkb/2014-15/boxscores/20141108_zc1e.xml?view=teamstats',
    # 'http://oua.ca/sports/mbkb/2014-15/boxscores/20141114_jyud.xml?view=teamstats','http://oua.ca/sports/mbkb/2014-15/boxscores/20141121_5m0y.xml?view=teamstats',
    # 'http://oua.ca/sports/mbkb/2014-15/boxscores/20141122_kkin.xml?view=teamstats','http://oua.ca/sports/mbkb/2014-15/boxscores/20141128_q4pf.xml?view=teamstats']
    q = get_links()
    a = scrape(q)
    df = pd.DataFrame(a)
    df = df.T
    df = df.replace('\-', ' -- ', regex=True).astype(object)
    df = df[['Away', 'FG Away', 'FG% Away', '3PT FG Away', '3PT FG% Away', 'FT Away', 'FT% Away', 'Rebounds Away',
             'Assists Away',
             'Turnovers Away', 'Points Off Turnovers Away', '2nd Chance Points Away', 'Points in the Paint Away',
             'Fastbreak Points Away', 'Bench Points Away',
             'Largest Lead Away', 'Time of Largest Lead Away', 'Home', 'FG Home',
             'FG% Home', '3PT FG Home', '3PT FG% Home', 'FT Home', 'FT% Home', 'Rebounds Home', 'Assists Home',
             'Turnovers Home',
             'Points Off Turnovers Home', '2nd Chance Points Home', 'Points in the Paint Home', 'Fastbreak Points Home',
             'Bench Points Home', 'Largest Lead Away', 'Time of Largest Lead Away', 'Trends Away', 'Winner', 'Winner 1st Qtr Pts',
             'Winner 2nd Qtr Pts', 'Winner 3rd Qtr Pts', 'Winner 4th Qtr Pts', 'Winner Total Pts', 'Loser', 'Loser 1st Qtr Pts', 'Loser 2nd Qtr Pts',
             'Loser 3rd Qtr Pts', 'Loser 4th Qtr Pts', 'Loser Total Pts']]

    df.to_csv('gbyg.csv', header=True)

    import pdb; pdb.set_trace()