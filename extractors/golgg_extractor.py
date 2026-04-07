from .base_extractor import BaseExtractor
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import requests
from urllib.parse import urljoin
from core.config import URLS

class GolggExtractor(BaseExtractor):
    def extrair_dados(self, url):
        data = []

        browser = webdriver.Chrome()
        browser.get('https://gol.gg/tournament/list/')

        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "table.table_list tr"))
        )

        main_html = browser.page_source
        browser.quit()

        soup = BeautifulSoup(main_html, 'html.parser')

        title = soup.title.text
        print(f"Acessado: {title}\n")

        table = soup.find('table', class_='table_list')
        leagues_links = table.find_all('a') 

        for league in leagues_links:
            link = league.get('href')
            full_link = urljoin("https://gol.gg/tournament/", link).replace("tournament-stats", "tournament-matchlist") # Criar o link com a lista de partidas
            tournament_resp = requests.get(full_link)
            
            if tournament_resp.status_code == 200:
                
                soup = BeautifulSoup(tournament_resp.text, 'html.parser')

                title = soup.title.text
                print(f"Acessado: {title}\n")

                matches_table = soup.find('table')
                rows = matches_table.find_all('tr')

                for row in rows:
                    cols = row.find_all('td')
                    if len(cols) == 7:
                        match_info = {"t1": None, "t2": None, "scr1": None, "scr2": None, "patch": None, "date": None}
                        match_info["t1"] = cols[1].text
                        match_info["t2"] = cols[3].text
                        match_info["scr1"] = cols[2].text.split('-')[0]
                        match_info["scr2"] = cols[2].text.split('-')[1]
                        match_info["patch"] = cols[5].text
                        match_info["date"] = cols[6].text
                        bd.append(match_info)
                
            else:
                print(f"Erro ao acessar a página. Código de status: {tournament_resp.status_code}")
    

print(pd.DataFrame(bd))


from bs4 import BeautifulSoup
import pandas as pd

bd = []

with open('tournament.html', 'r', encoding='utf-8') as arquivo:
    html = arquivo.read()

soup = BeautifulSoup(html, 'html.parser')

title = soup.title.text
print(f"Acessado: {title}\n")

matches_table = soup.find('table')
rows = matches_table.find_all('tr')

for row in rows:
    cols = row.find_all('td')
    if len(cols) == 7:
        match_info = {"t1": None, "t2": None, "scr1": None, "scr2": None, "patch": None, "date": None}
        match_info["t1"] = cols[1].text
        match_info["t2"] = cols[3].text
        match_info["scr1"] = cols[2].text.split('-')[0]
        match_info["scr2"] = cols[2].text.split('-')[1]
        match_info["patch"] = cols[5].text
        match_info["date"] = cols[6].text
        bd.append(match_info)

print(pd.DataFrame(bd))