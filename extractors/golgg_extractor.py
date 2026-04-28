from extractors.base_extractor import BaseExtractor
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import requests
import pandas as pd
from urllib.parse import urljoin
from core.config import URLS, HEADERS_PADRAO
import time

class GolggExtractor(BaseExtractor):
    def __init__(self, url_home):
        self.sessao = requests.Session()
        self.url_home = url_home
        self.sessao.headers.update(HEADERS_PADRAO)


    def _extract_leagues(self):
        leagues_links = []

        browser = webdriver.Chrome()
        browser.get(self.url_home + "tournament/list/")

        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "table.table_list tr"))
        )

        html = browser.page_source
        browser.quit()

        soup = BeautifulSoup(html, 'html.parser')

        table = soup.find('table', class_='table_list')
        links = table.find_all('a')

        for a in links:
            link = a.get('href')
            full_link = urljoin(self.url_home + "tournament/", link).replace("tournament-stats", "tournament-matchlist")
            leagues_links.append({
                "league": a.text,
                "link": full_link
            })
        
        return leagues_links
    
    def _extract_matches(self, url_league):
        matches = []
        tournament_resp = requests.get(url_league)
        soup = BeautifulSoup(tournament_resp.text, 'html.parser')
        

        title = soup.title.text
        print(f"Torneio: {title}")

        matches_table = soup.find('table')
        rows = matches_table.find_all('tr')

        n_matches = len(rows)
        i = 1
        
        for row in rows:
            cols = row.find_all('td')
            if cols:
                if cols[5].text:
                    print(f"Match: {i}/{n_matches}")
                    time_init = time.time()
                    game = row.find('a')
                    link = urljoin(self.url_home, game.get('href').replace("page-game", "page-summary"))
                    matches.append({
                        'match': game.text,
                        'team1': cols[1].text,
                        'team2': cols[3].text,
                        'score': cols[2].text,
                        'patch': cols[5].text,
                        'date': cols[6].text,
                        'url_match': link,
                        'games': self._extract_games(link)
                        })
        
                    time_end = time.time()
                    i += 1
                    print(f"Tempo total: {time_end - time_init} segundos")

        return matches


    def _extract_games(self, url_game):
        games = []
        games_resp = requests.get(url_game, headers=HEADERS_PADRAO)
        soup = BeautifulSoup(games_resp.text, 'html.parser')
        games_nav = soup.find(id='gameMenuToggler')
        games_link = games_nav.find_all('a')
        best_of = None
        h1s = soup.find_all('h1')
        for h1 in h1s:
            if h1.text in ('BO1', 'BO3', 'BO5'):
                best_of = h1.text[-1]
        
        n_games = len(games_link) - 2
        i = 1
        for a_link in games_link:
            game = {}
            if 'game' in a_link.text.lower():
                print(f"Game: {i}/{n_games}")
                game['game'] = a_link.text.lower().split('game')[1]
                game['best_of'] = best_of
                game_link = urljoin(self.url_home, a_link.get('href'))
                game_resp = requests.get(game_link, headers=HEADERS_PADRAO)
                soup_game = BeautifulSoup(game_resp.text, 'html.parser')
                game['time'] = soup_game.find('div', class_='col-6 text-center').find('h1').text
                
                
                team1_cond = soup_game.find('div', class_= "col-12 blue-line-header").text
                team2_cond = soup_game.find('div', class_= "col-12 red-line-header").text
                
                game['t1'] = team1_cond.split('-')[0]
                game['t2'] = team2_cond.split('-')[0]
                if 'win' in team1_cond.split('-')[1].lower():
                    game['winner'] = team1_cond.split('-')[0]
                else:
                    game['winner'] = team2_cond.split('-')[0]
                
                team1_info = soup_game.find_all('div', class_='col-12 col-sm-6')[0]
                team2_info = soup_game.find_all('div', class_='col-12 col-sm-6')[1]

                team1_stats = team1_info.find_all('div', class_='col-2')
                team2_stats = team2_info.find_all('div', class_='col-2')

                game['t1_kills'] = team1_stats[0].find('span').text
                game['t1_towers'] = team1_stats[1].find('span').text
                game['t1_dragons'] = team1_stats[2].find('span').text
                game['t1_nashors'] = team1_stats[3].find('span').text
                game['t1_gold'] = team1_stats[4].find('span').text

                game['t2_kills'] = team2_stats[0].find('span').text
                game['t2_towers'] = team2_stats[1].find('span').text
                game['t2_dragons'] = team2_stats[2].find('span').text
                game['t2_nashors'] = team2_stats[3].find('span').text
                game['t2_gold'] = team2_stats[4].find('span').text

                team1_bans = team1_info.find_all("div", class_="row")[2].find("div", class_="col-10").find_all("img")
                team1_champ_bans = [champ.get('alt') for champ in team1_bans]
                
                game['t1_bans'] = team1_champ_bans

                team2_bans = team2_info.find_all("div", class_="row")[2].find("div", class_="col-10").find_all("img")
                team2_champ_bans = [champ.get('alt') for champ in team2_bans]
                
                game['t2_bans'] = team2_champ_bans
                
                team1_comp = soup_game.find_all('table', class_="playersInfosLine footable toggle-square-filled")[0].find_all('tr', recursive=False)
                team2_comp = soup_game.find_all('table', class_="playersInfosLine footable toggle-square-filled")[1].find_all('tr', recursive=False)
                
                game['t1_picks'] = [champ.find('td').find('img').get('alt') for champ in team1_comp]
                game['t2_picks'] = [champ.find('td').find('img').get('alt') for champ in team2_comp]

                game['t1_players'] = [champ.find('td').find('a', class_='link-blanc').text for champ in team1_comp]
                game['t2_players'] = [champ.find('td').find('a', class_='link-blanc').text for champ in team2_comp]
            
                games.append(game)
                i += 1
        
        return games
            
    def teste(self, url):
        print(self._extract_games(url))

    def extract(self):
        data = []
        leagues = self._extract_leagues()

        n_leagues = len(leagues)
        i = 1
        for league in leagues:
            print(f"League: {i}/{n_leagues}")
            dt = {}
            league_link = league["link"]
            league_matches = self._extract_matches(league_link)
            dt['league'] = league['league']
            dt['league_link'] = league_link
            dt['matches'] = league_matches
            data.append(dt)
            i += 1
        
        print(data)
        pd.DataFrame(data).to_csv("games_lol.csv")
        

