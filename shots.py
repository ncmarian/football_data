from selenium import webdriver
from datetime import date, timedelta
import requests
from bs4 import BeautifulSoup
import csv

def date_range(start_date, end_date):
    for n in range((end_date - start_date).days):
        yield (start_date + timedelta(n)).strftime('%Y%m%d')

def get_games_id (start_year, start_month, start_day, end_year, end_month, end_day):
    
    games_id = []
    dates = []

    for item in date_range(date(start_year, start_month, start_day), date(end_year, end_month, end_day)):
        dates.append(item)

    driver = webdriver.Chrome()

    for day in dates:
        driver.get('http://www.espn.com.ar/futbol/resultados/_/liga/arg.1/fecha/' + day)

        game_link_driver = driver.find_elements_by_name('&lpos=soccer:scoreboard:resumen')

        game_links = []

        for i in range(len(game_link_driver)):
            game_links.append(game_link_driver[i].get_attribute('href'))

        for game in game_links:
            games_id.append(game[46:53])

        driver.quit

    return games_id

def get_game_shots (id):

    url = 'http://www.espn.com.ar/futbol/numeritos?juegoId=' + str(id)

    print id

    r = requests.get(url)
    soup = BeautifulSoup(r.content,'html.parser')
    
    teams_html = soup.find_all("div", {"class":"possession"})

    if not len(teams_html):
        return None

    for item in teams_html:
        name = item.find_all('span',{"class":"team-name"})

    team_names = [n.contents[0] for n in name]

    home_team_raw = team_names[0]
    away_team_raw = team_names[1]

    if 'Atl Tucum' in home_team_raw:
        home_team = 'TUC'
    else:
        home_team = home_team_raw

    if 'Atl Tucum' in away_team_raw:
        away_team = 'TUC'
    else:
        away_team = away_team_raw

    # Home Score
    home_html = soup.find_all("span", {"class":"score icon-font-after"})
    if not len(home_html):
        return None

    home_contents = [p.contents[0] for p in home_html]

    if home_contents[0] == '\n':
        return None

    home_goals = int(home_contents[0].strip())

    # Away Score
    away_html = soup.find_all("span", {"class":"score icon-font-before"})

    away_contents = [p.contents[0] for p in away_html]

    away_goals = int(away_contents[0].strip())

    #Shots

    shots_html = soup.find_all("div", {"class":"shots"})

    if not len(shots_html):
        return None

    for item in shots_html:
        shots_data = item.find_all('span',{"class":"number"})

    shots_contents = [s.contents[0] for s in shots_data]

    shots_home = shots_contents[0].split()
    shots_away = shots_contents[1].split()

    shots_home_nobrackets = shots_home[1][1:-1]
    shots_away_nobrackets = shots_away[1][1:-1]

    shots_home_num = [int(shots_home[0]),int(shots_home_nobrackets)]
    shots_away_num = [int(shots_away[0]),int(shots_away_nobrackets)]

    home_totalshots = shots_home_num[0]
    away_totalshots = shots_away_num[0]
    home_shotsgoal = shots_home_num[1]
    away_shotsgoal = shots_away_num[1]

    game = [home_team, away_team, home_goals, away_goals, home_totalshots,
            away_totalshots, home_shotsgoal, away_shotsgoal]

    return game

def write_to_csv (games):
      writer = csv.writer(csv_file)
      writer.writerows(games)

# Program
games_id = get_games_id (2016, 2, 1, 2016, 4, 26)

list_of_games_data = []

for game in games_id:
    game_data = get_game_shots(game)
    if game_data:
        list_of_games_data.append(game_data)

row_names = ['home_name', 'away_name', 'home_goals', 'away_goals',
            'home_totalshots', 'away_totalshots',
            'home_shotsgoal', 'away_shotsgoal']

with open('shots_data.csv', 'w') as csv_file:
    write_to_csv([row_names])

    for game in list_of_games_data:
        write_to_csv([game])