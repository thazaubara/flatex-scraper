import credentials
from selenium import webdriver
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime

# https://www.youtube.com/watch?v=Xjv1sY630Uc&list=PLzMcBGfZo4-n40rB1XaJ0ak1bemvlqumQ

def scrape_flatex():
    username = credentials.username
    password = credentials.password
    timeout = 5
    headless = False

    if headless:
        options = webdriver.ChromeOptions()
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--start-maximized")
        options.add_argument("--headless")

        driver = webdriver.Chrome(options=options)
        # driver.set_window_size(1920, 1080)
    else:
        driver = webdriver.Chrome()

    driver.get("https://www.flatex.at")

    loginbutton = driver.find_element(By.CLASS_NAME, "shape-login")
    loginbutton.click()
    txt_username = driver.find_element(By.NAME, "tx_flatexaccounts_singlesignonbanking[uname_app]")
    txt_username.send_keys(username)
    txt_password = driver.find_element(By.NAME, "tx_flatexaccounts_singlesignonbanking[password_app]")
    txt_password.send_keys(password)
    txt_password.send_keys(Keys.ENTER)

    driver.get("https://konto.flatex.at/banking-flatex.at/depositStatementFormAction.do")

    # time.sleep(5)
    # title = driver.find_element(By.ID, "titleAnchor")

    title = WebDriverWait(driver, timeout).until(EC.visibility_of_element_located((By.ID, "titleAnchor")))
    print(title.text)

    # amount = driver.find_element(By.CLASS_NAME, "PositiveAmount")
    # print(amount.text)

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

    positions = []

    def to_float(my_input):
        try:
            return float(my_input.split()[0].replace(".", "").replace(",", "."))
        except TypeError as e:
            print(my_input)
            print(e.with_traceback())

    def to_date(my_input):
        input_format = "%d.%m.%Y | %H:%M"
        return datetime.strptime(my_input, input_format)

    index = 0
    while True:
        try:
            pos = Position()
            # X(IE)-MSCI WORLD 1C (XDWD)
            pos.bezeichnung = driver.find_element(By.CSS_SELECTOR, f"#TID-1328765475_{index}-0 > td.C0.First > div").text
            # IE00BJ0KDQ92
            # #depositStatementForm_depositStatementTable_childrenI5I
            # #depositStatementForm_depositStatementTable_childrenI10I
            pos.isin = driver.find_element(By.CSS_SELECTOR, f"#depositStatementForm_depositStatementTable_childrenI{index*5}I").text
            # A1XB5U
            pos.wkn = driver.find_element(By.CSS_SELECTOR, f"#TID-1328765475_{index}-1 > td.C0.First > table > tbody > tr > td.M2").text
            # Fonds
            pos.kategorie = driver.find_element(By.CSS_SELECTOR, f"#TID-1328765475_{index}-2 > td.C0.First").text
            # XXX,295 Stk.
            pos.stk = to_float(driver.find_element(By.CSS_SELECTOR, f"#TID-1328765475_{index}-0 > td.C1 > span").text)
            # XXX,105 EUR
            pos.einstandskurs = to_float(driver.find_element(By.CSS_SELECTOR, f"#TID-1328765475_{index}-1 > td.C1 > span").text)
            # Clearstream Lux.
            pos.lagerst = driver.find_element(By.CSS_SELECTOR, f"#TID-1328765475_{index}-2 > td.C1").text
            # Tradegate
            pos.boerse = driver.find_element(By.CSS_SELECTOR, f"#TID-1328765475_{index}-0 > td.C2 > div").text
            # 28.07.2023 | 21:58
            pos.datum = to_date(driver.find_element(By.CSS_SELECTOR, f"#TID-1328765475_{index}-1 > td.C2").text)
            # XXX,3621 EUR
            pos.letzter_kurs = to_float(driver.find_element(By.CSS_SELECTOR, f"#TID-1328765475_{index}-0 > td.C3 > span").text)
            # 0,4778
            pos.vortag = to_float(driver.find_element(By.CSS_SELECTOR, f"#TID-1328765475_{index}-1 > td.C3 > span").text)
            # 0,556 %
            pos.vortag_perc = to_float(driver.find_element(By.CSS_SELECTOR, f"#TID-1328765475_{index}-2 > td.C3 > span").text)
            # XXX.829,41 EUR
            pos.aktueller_wert = to_float(driver.find_element(By.CSS_SELECTOR, f"#TID-1328765475_{index}-0 > td.C4 > span").text)
            # XXX.289,50 EUR
            pos.einstandswert = to_float(driver.find_element(By.CSS_SELECTOR, f"#TID-1328765475_{index}-1 > td.C4 > span").text)
            # XXX.539,91 EUR
            pos.entwicklung_abs = to_float(driver.find_element(By.CSS_SELECTOR, f"#TID-1328765475_{index}-0 > td.C5 > span").text)
            # XX,99 %
            pos.entwicklung_perc = to_float(driver.find_element(By.CSS_SELECTOR, f"#TID-1328765475_{index}-1 > td.C5 > span").text)

            positions.append(pos)

        except Exception as e:
            # NoSuchElementException ... sowohl bei ende von array, als auch bei not found. also wurscht.
            print(f"{index} positions found.")
            if index == 0:
                print(e.with_traceback())
                # print(driver.page_source)
            break
        index += 1

    for pos in positions:
        pos.print_all()

scrape_flatex()


