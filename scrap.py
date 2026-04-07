from bs4 import BeautifulSoup
from urllib.parse import urljoin
import requests
import pandas as pd
from core.config import URLS, HEADERS_PADRAO
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

navegador = webdriver.Chrome()
navegador.get('https://gol.gg/tournament/list/')

WebDriverWait(navegador, 10).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, "table.table_list tr"))
)

html_completo = navegador.page_source
navegador.quit()

bd = []

soup = BeautifulSoup(html_completo, 'html.parser')

title = soup.title.text
i_progress = 1
print(f"Acessado: {title}\n")

table = soup.find('table', class_='table_list')
links = table.find_all('a')

for a in links:
    link = a.get('href')
    link_full = urljoin("https://gol.gg/tournament/", link).replace("tournament-stats", "tournament-matchlist")
    tournament_resp = requests.get(link_full)
    
    if tournament_resp.status_code == 200:

        soup = BeautifulSoup(tournament_resp.text, 'html.parser')

        title = soup.title.text
        print(f"Torneio: {title}")

        matches_table = soup.find('table')
        rows = matches_table.find_all('tr')

        for row in rows:
            cols = row.find_all('td')
            if len(cols) == 7:
                if cols[5].text:
                    match_info = {}
                    match_info["tournament"] = title
                    match_info["team1"] = cols[1].text
                    match_info["team2"] = cols[3].text
                    match_info["score1"] = cols[2].text.split('-')[0]
                    match_info["score2"] = cols[2].text.split('-')[1]
                    match_info["patch"] = cols[5].text
                    match_info["date"] = cols[6].text
                
                    game = row.find('a')
                    if game:
                        link = game.get('href')

                        link_game = urljoin("https://gol.gg/", link).replace("page-game", "page-summary")
                        resp_game = requests.get(link_game, headers=HEADERS_PADRAO)

                        soup = BeautifulSoup(resp_game.text, 'html.parser')
                        h1s = soup.find_all('h1')

                        for h1 in h1s:
                            if h1.text in ('BO1', 'BO3', 'BO5'):
                                best_off = h1.text[-1]
                        
                        infos_stats = soup.find('div', class_='row pt-4')
                        
                        infos = infos_stats.find_all('span', class_='score-box')
                        infos_list = [inf.text.strip() for inf in infos]
                        match_info['team1_kills'] = infos_list[0]
                        match_info['team1_towers'] = infos_list[1]
                        match_info['team1_dragons'] = infos_list[2]
                        match_info['team1_nashors'] = infos_list[3]

                        match_info['team2_kills'] = infos_list[4]
                        match_info['team2_towers'] = infos_list[5]
                        match_info['team2_dragons'] = infos_list[6]
                        match_info['team2_nashors'] = infos_list[7]

                        games = soup.find_all('div', class_='row pb-1')

                        for i in range(len(games)):
                            game = games[i]
                            champs = [img.get('alt') for img in game.find_all('img')]
                            gold_difference = game.find('span', class_='text_victory').text
                            match_info[f'p{i+1}_gold_difference'] = gold_difference

                            bans1 = champs[0:5]
                            picks1 = champs[5:10]
                            bans2 = champs[10:15]
                            picks2 = champs[15:20]

                            match_info[f'p{i+1}_team1_bans'] = bans1
                            match_info[f'p{i+1}_team1_picks'] = picks1

                            match_info[f'p{i+1}_team2_bans'] = bans2
                            match_info[f'p{i+1}_team2_picks'] = picks2

                    bd.append(match_info)
    else:
        print(f"Erro ao acessar a página. Código de status: {tournament_resp.status_code}")
    print(f"Progresso: {i_progress}/{len(links)}")
    i_progress += 1
    
bd_df = pd.DataFrame(bd).to_csv("bd_em_csv.csv")
print(pd.DataFrame(bd))
