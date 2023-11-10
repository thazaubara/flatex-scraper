import sys
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timezone
import mysql.connector as mariadb
from mysql.connector import Error
from selenium.webdriver.common.action_chains import ActionChains

# https://www.youtube.com/watch?v=Xjv1sY630Uc&list=PLzMcBGfZo4-n40rB1XaJ0ak1bemvlqumQ
# https://selenium-python.readthedocs.io/index.html
import credentials

DB_HOST = credentials.DB_HOST
DB_PORT = credentials.DB_PORT
DB_NAME = credentials.DB_NAME
DB_USER = credentials.DB_USER
DB_PASS = credentials.DB_PASS
FLATEX_USER = credentials.FLATEX_USER
FLATEX_PASS = credentials.FLATEX_PASS
HEADLESS = False

utc_timestamp = datetime.utcnow()

class Position:
    def __init__(self):
        self.bezeichnung = None
        self.isin = None
        self.wkn = None
        self.kategorie = None
        self.stk = None
        self.einstandskurs = None
        self.lagerst = None
        self.boerse = None
        self.datum = None
        self.letzter_kurs = None
        self.vortag = None
        self.vortag_perc = None
        self.aktueller_wert = None
        self.einstandswert = None
        self.entwicklung_abs = None
        self.entwicklung_perc = None

    def __str__(self):
        return f"{self.bezeichnung} ({self.letzter_kurs}): {self.aktueller_wert}"

    def print_all(self):
        print(f"\nBezeichnung:    {self.bezeichnung}")
        print(f"ISIN:           {self.isin}")
        print(f"WKN:            {self.wkn}")
        print(f"Kategorie:      {self.kategorie}")
        print(f"Stk.:           {self.stk}")
        print(f"Einstandskurs:  {self.einstandskurs}")
        print(f"Lagerstelle:    {self.lagerst}")
        print(f"Börse:          {self.boerse}")
        print(f"Datum:          {self.datum}")
        print(f"Letzter Kurs:   {self.letzter_kurs}")
        print(f"Vortag +/-:     {self.vortag}")
        print(f"Vortag %:       {self.vortag_perc}")
        print(f"Aktueller Wert: {self.aktueller_wert}")
        print(f"Einstandswert:  {self.einstandswert}")
        print(f"Entw. Abs:      {self.entwicklung_abs}")
        print(f"Entw. %:        {self.entwicklung_perc}")

    def generate_execstring(self):
        table = credentials.DB_TABLE
        utc_date = self.datum.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S.%f")

        execstring = f"INSERT INTO `{table}` (`timestamp_utc`, `date_utc`, `bezeichnung`, `isin`, `wkn`, `kategorie`, `stk`, `einstandskurs`, `lagersts`, `boerse`, `letzter_kurs`, `vortag`, `vortag_perc`, `aktueller_wert`, `einstandswert`, `entwicklung_abs`, `entwicklung_perc`) " \
                     f"VALUES ('{utc_timestamp}', '{utc_date}', '{self.bezeichnung}', '{self.isin}', '{self.wkn}', '{self.kategorie}', {self.stk}, {self.einstandskurs}, '{self.lagerst}', '{self.boerse}', {self.letzter_kurs}, {self.vortag}, {self.vortag_perc}, {self.aktueller_wert}, {self.einstandswert}, {self.entwicklung_abs}, {self.entwicklung_perc})"

        return execstring

def STOPHERE(text=""):
    pressed = input(f"STOPPING HERE -> {text}")

def TOFILE(name, text):
    f = open(name, "a")
    f.write(text)
    f.close()

def SCREENSHOT(driver, name):
    driver.save_screenshot(name)

def info():
    execstring = f"SELECT table_schema 'DB Name',table_rows,ROUND(SUM(data_length + index_length) / 1024 / 1024, 1) 'DB Size in MB' FROM information_schema.tables WHERE table_schema = '{credentials.DB_NAME}'"
    cursor.execute(execstring)
    all = cursor.fetchall()
    records = all[0][1]
    size_mb = all[0][2]
    return records, size_mb

def scrape_flatex(headless=False):
    timeout = 2

    options = webdriver.ChromeOptions()
    options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36")
    options.add_argument("--window-size=1400,1000")

    options.add_argument("--window-position=1800,0")  # just for testing, open window on other screen

    if headless:
        options.add_argument("--start-maximized")
        options.add_argument("--headless")

    driver = webdriver.Chrome(options=options)
    width = driver.get_window_size().get("width")
    height = driver.get_window_size().get("height")
    print(f"driver set to {width}x{height}")

    # GO TO SITE
    # base_url = "https://flatex.at"
    base_url = "https://konto.flatex.at/login.at/loginIFrameFormAction.do"
    print(f"Loading {base_url}")
    driver.get(base_url)

    # FILL CREDENTIALS IN POPUP
    # STOPHERE("fill credentials")

    txt_username = WebDriverWait(driver, timeout).until(EC.visibility_of_element_located((By.ID, "loginIFrameForm_txtUserId_container")))
    txt_username.click()
    actions = ActionChains(driver)
    actions.send_keys(FLATEX_USER)
    actions.perform()

    txt_username = WebDriverWait(driver, timeout).until(EC.visibility_of_element_located((By.ID, "loginIFrameForm_txtPassword_container")))
    txt_username.click()
    actions.send_keys(FLATEX_PASS)
    actions.perform()

    login_button = WebDriverWait(driver, timeout).until(EC.visibility_of_element_located((By.ID, "btnSubmitForm")))
    login_button.click()

    driver.get("https://konto.flatex.at/banking-flatex.at/depositStatementFormAction.do")
    time.sleep(5)  # give it time to load, yo!

    title = WebDriverWait(driver, timeout).until(EC.visibility_of_element_located((By.ID, "titleAnchor")))
    print(f"{title.text}:")


    def to_float(my_input):
        try:
            return float(my_input.split()[0].replace(".", "").replace(",", "."))
        except TypeError as e:
            print(my_input)
            print(e.with_traceback())

    def to_date(my_input):
        input_format = "%d.%m.%Y | %H:%M"
        return datetime.strptime(my_input, input_format)

    positions = []
    index = 0
    while True:
        try:
            pos = Position()

            pos.bezeichnung = driver.find_element(By.CSS_SELECTOR, f"#TID-1328765475_{index}-0 > td.C0.First > div").text  # X(IE)-MSCI WORLD 1C (XDWD)
            pos.isin = driver.find_element(By.CSS_SELECTOR, f"#depositStatementForm_depositStatementTable_childrenI{index*5}I").text  # IE00BJ0KDQ92
            pos.wkn = driver.find_element(By.CSS_SELECTOR, f"#TID-1328765475_{index}-1 > td.C0.First > table > tbody > tr > td.M2").text  # A1XB5U
            pos.kategorie = driver.find_element(By.CSS_SELECTOR, f"#TID-1328765475_{index}-2 > td.C0.First").text  # Fonds
            pos.stk = to_float(driver.find_element(By.CSS_SELECTOR, f"#TID-1328765475_{index}-0 > td.C1 > span").text)  # 403,295 Stk.
            pos.einstandskurs = to_float(driver.find_element(By.CSS_SELECTOR, f"#TID-1328765475_{index}-1 > td.C1 > span").text)  # 75,105 EUR
            pos.lagerst = driver.find_element(By.CSS_SELECTOR, f"#TID-1328765475_{index}-2 > td.C1").text  # Clearstream Lux.
            pos.boerse = driver.find_element(By.CSS_SELECTOR, f"#TID-1328765475_{index}-0 > td.C2 > div").text  # Tradegate
            pos.datum = to_date(driver.find_element(By.CSS_SELECTOR, f"#TID-1328765475_{index}-1 > td.C2").text)  # 28.07.2023 | 21:58
            pos.letzter_kurs = to_float(driver.find_element(By.CSS_SELECTOR, f"#TID-1328765475_{index}-0 > td.C3 > span").text)  # 86,3621 EUR
            try:  # scheinbar gegen ende des tage keine werte
                pos.vortag = to_float(driver.find_element(By.CSS_SELECTOR, f"#TID-1328765475_{index}-1 > td.C3 > span").text)  # 0,4778
                pos.vortag_perc = to_float(driver.find_element(By.CSS_SELECTOR, f"#TID-1328765475_{index}-2 > td.C3 > span").text)  # 0,556 %
            except:
                pos.vortag = "NULL"
                pos.vortag_perc = "NULL"
            pos.aktueller_wert = to_float(driver.find_element(By.CSS_SELECTOR, f"#TID-1328765475_{index}-0 > td.C4 > span").text)  # 34.829,41 EUR
            pos.einstandswert = to_float(driver.find_element(By.CSS_SELECTOR, f"#TID-1328765475_{index}-1 > td.C4 > span").text)  # 30.289,50 EUR
            pos.entwicklung_abs = to_float(driver.find_element(By.CSS_SELECTOR, f"#TID-1328765475_{index}-0 > td.C5 > span").text)  # 4.539,91 EUR
            pos.entwicklung_perc = to_float(driver.find_element(By.CSS_SELECTOR, f"#TID-1328765475_{index}-1 > td.C5 > span").text)  # 14,99 %

            positions.append(pos)

        except Exception as e:  # gewollt. wenn keine zeilen mehr da sind, beende loop.
            print(f"{index} positions found.")
            if index == 0:
                print(e.with_traceback())
            break
        index += 1

    driver.quit()
    return positions

# SCRAPE FLATEX
current_positions = scrape_flatex(headless=HEADLESS)

for position in current_positions:
    position.print_all()
print()

# CONNECT DATABASE
cursor = None
connection = None
try:
    connection = mariadb.connect(host=DB_HOST, user=DB_USER, port=DB_PORT, password=DB_PASS)
    if connection.is_connected():
        cursor = connection.cursor()
        cursor.execute(f"use {DB_NAME};")
        print(f"DB connected: {DB_USER}@{DB_HOST}:{DB_PORT} DB:{DB_NAME}")
    else:
        print("No connection MySQL")
        exit()
except Error as e:
    print("Error while connecting to MySQL", e)

# CHECK DATABASE
# db_records, db_size = info()
# print(f"Database size: {db_size} with {db_records} records")


# INSERT INTO DATABASE
print("Inserting into database...")
for position in current_positions:
    try:
        cursor.execute(position.generate_execstring())
        connection.commit()
        cursor.reset()
        print(f"DB upload of {position} done.")
    except Exception as e:
        print(position.generate_execstring())
        print(e.with_traceback())

# CLEANUP
connection.close()





