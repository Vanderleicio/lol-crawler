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