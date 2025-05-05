import csv
import time
import os
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def scrape_odds(output_csv: str = 'maxbet_meciuri.csv', scroll_pause: float = 1.0, max_scrolls: int = 50):
    """
    Accesează site-ul MaxBet și extrage cotele 1, X, 2 pentru toate meciurile de fotbal afișate,
    executând scroll până la încarcarea completă a conținutului, apoi salvează rezultatele într-un fișier CSV.
    Parametri:
        output_csv (str)   – Numele fișierului CSV de ieșire (implicit 'maxbet_cote.csv')
        scroll_pause (float) – Timp de așteptare între scroll-uri (secunde)
        max_scrolls (int)  – Numărul maxim de scroll-uri pentru a preveni bucle infinite
    """
    url = "https://www.maxbet.ro/ro/pariuri-sportive?sport=2"
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_dir, output_csv)

    options = webdriver.ChromeOptions()
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('window-size=1920,1080')
    prefs = {"profile.default_content_setting_values.notifications": 2}
    options.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 20)

    try:
        print(f"🌐 Deschid pagina: {url}")
        driver.get(url)

        # Închide pop-up-uri și acceptă cookies
        try:
            later_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH,
                    "//*[translate(normalize-space(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz')='poate mai târziu']"
                ))
            )
            later_btn.click()
            print("Pop-up notificări interne închis")
            time.sleep(0.5)
        except:
            print("Niciun pop-up intern de notificări")
         # --- Acceptă cookies (fallback) ---
        try:
            cook_btn = driver.find_element(
                By.XPATH,
                "//button[contains(translate(., 'ĂÂÎȘȚ','ÂÎȘȚĂ'), 'Acceptă cookies')]"
            )
            cook_btn.click()
            print("Cookies acceptate (fallback)")
            time.sleep(0.5)
        except:
            pass


        # Filtru "Toate"
        try:
            toate_btn = wait.until(EC.element_to_be_clickable((
                By.XPATH,
                "//div[contains(@class,'filter-container')]//div[contains(@class,'filter-item') and normalize-space()='Toate']"
            )))
            toate_btn.click()
            print("Filtru 'Toate' activat")
            time.sleep(1)
        except:
            print("Filtru 'Toate' nu a fost găsit sau e deja activ")

        # Scroll pentru a încărca toate meciurile
        last_height = driver.execute_script("return document.body.scrollHeight")
        scroll_count = 0
        while scroll_count < max_scrolls:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(scroll_pause)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                print(f"🔄 Conținut complet încărcat după {scroll_count} scroll-uri.")
                break
            last_height = new_height
            scroll_count += 1
        else:
            print(f"Max scroll-uri ({max_scrolls}) atinse, poate nu s-au încărcat toate meciurile.")

        # Așteaptă apare evenimentele
        wait.until(EC.presence_of_element_located((By.TAG_NAME, 'event')))
        matches = driver.find_elements(By.TAG_NAME, 'event')
        print(f"🔍 Găsite {len(matches)} evenimente de fotbal după scroll")

        # Scrie CSV
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['data', 'echipa1', 'echipa2', 'cota_1', 'cota_X', 'cota_2'])

            for idx, match in enumerate(matches, start=1):
                # Data
                try:
                    full_time = match.find_element(By.CSS_SELECTOR, 'div.event__header div.time').text.strip()
                    data = full_time.splitlines()[0]
                except:
                    data = ''
                # Echipe
                comps = match.find_element(By.CSS_SELECTOR, 'div.event__wrapper div.general__competitors').text.strip()
                team1, team2 = comps.splitlines()
                # Cote
                try:
                    odd_spans = match.find_elements(
                        By.CSS_SELECTOR, 'div.market__wrapper .market__outcome span.outcome.centered'
                    )[:3]
                    odds = [s.text.strip() for s in odd_spans]
                except:
                    odds = ['', '', '']
                c1, cX, c2 = (odds + ['', '', ''])[:3]

                print(f"Meci #{idx}: {data} | {team1} vs {team2} | cote: 1={c1}, X={cX}, 2={c2}")
                print('-'*40)
                writer.writerow([data, team1, team2, c1, cX, c2])

        print(f"Toate meciurile au fost salvate în '{csv_path}'")

    finally:
        driver.quit()


if __name__ == '__main__':
    scrape_odds('maxbet_meciuri.csv')
