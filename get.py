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

with open('golgg.html', 'w', encoding='utf-8') as arquivo:
    arquivo.write(html_completo)
    
print("HTML salvo")