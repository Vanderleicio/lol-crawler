from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urljoin
import requests
from core.config import URLS, HEADERS_PADRAO

bd = []

with open('tournament.html', 'r', encoding='utf-8') as arquivo:
    html = arquivo.read()

soup = BeautifulSoup(html, 'html.parser')

title = soup.title.text
print(f"Acessado: {title}\n")

matches_table = soup.find('table')
rows = matches_table.find_all('tr')

for row in rows:
    game = row.find('a')
    print(game)

    if game:
        infos_bd = {}
        link = game.get('href')
        link_game = urljoin("https://gol.gg/", link)
        resp_game = requests.get(link_game, headers=HEADERS_PADRAO)
        print(resp_game.status_code)

        soup = BeautifulSoup(resp_game.text, 'html.parser')
        h1s = soup.find_all('h1')

        for h1 in h1s:
            if h1.text in ('BO1', 'BO3', 'BO5'):
                best_off = h1.text[-1]
        
        infos_stats = soup.find('div', class_='row pt-4')
        
        infos = infos_stats.find_all('span', class_='score-box')
        infos_list = [inf.text.strip() for inf in infos]
        infos_bd['team1_kills'] = infos_list[0]
        infos_bd['team1_towers'] = infos_list[1]
        infos_bd['team1_dragons'] = infos_list[2]
        infos_bd['team1_nashors'] = infos_list[3]

        infos_bd['team2_kills'] = infos_list[4]
        infos_bd['team2_towers'] = infos_list[5]
        infos_bd['team2_dragons'] = infos_list[6]
        infos_bd['team2_nashors'] = infos_list[7]

        games = soup.find_all('div', class_='row pb-1')

        for i in range(len(games)):
            game = games[i]
            champs = [img.get('alt') for img in game.find_all('img')]
            gold_difference = game.find('span', class_='text_victory').text
            infos_bd[f'p{i+1}_gold_difference'] = gold_difference

            bans1 = champs[0:5]
            picks1 = champs[5:10]
            bans2 = champs[10:15]
            picks2 = champs[15:20]

            infos_bd[f'p{i+1}_team1_bans'] = bans1
            infos_bd[f'p{i+1}_team1_picks'] = picks1

            infos_bd[f'p{i+1}_team2_bans'] = bans2
            infos_bd[f'p{i+1}_team2_picks'] = picks2
            

        print(infos_bd)
        break
