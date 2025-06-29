from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.chrome.options import Options
from pathlib import Path
import csv
import os
import time
import re
import sys

def get_place_prefecture(place):
    if place == "小倉":
        return "北海道"
    elif place == "前橋":
        return "群馬"
    elif place == "青森":
        return "青森"
    elif place == "高知":
        return "高知"
    elif place == "佐世保":
        return "長崎"
    elif place == "玉野":
        return "岡山"
    elif place == "奈良":
        return "奈良"
    elif place == "武雄":
        return "佐賀"
    elif place == "西武園":
        return "埼玉"
    elif place == "大垣":
        return "岐阜"
    elif place == "弥彦":
        return "新潟"
    elif place == "別府":
        return "大分"
    elif place == "宇都宮":
        return "栃木"
    elif place == "松阪":
        return "三重"
    elif place == "松戸":
        return "千葉"
    elif place == "川崎":
        return "神奈川"
    elif place == "伊東":
        return "静岡"
    elif place == "松山":
        return "愛媛"
    elif place == "豊橋":
        return "愛知"
    elif place == "四日市":
        return "三重"
    elif place == "函館":
        return "北海道"
    elif place == "名古屋":
        return "愛知"
    elif place == "向日町":
        return "京都"
    elif place == "平塚":
        return "神奈川"
    elif place == "久留米":
        return "福岡"
    elif place == "小松島":
        return "徳島"
    elif place == "岸和田":
        return "大阪"
    elif place == "高松":
        return "香川"
    elif place == "静岡":
        return "静岡"
    elif place == "京王閣":
        return "東京"
    elif place == "いわき平":
        return "福島"
    elif place == "岐阜":
        return "岐阜"
    elif place == "熊本":
        return "熊本"
    else:
        return "不明"
    
def get_area(place):
    if (place in ["北海道", "青森", "岩手", "宮城", "秋田", "山形", "福島"]):
        return "北日本"
    elif (place in ["新潟", "長野", "東京", "栃木", "群馬", "茨城", "埼玉", "山梨"]):
        return "関東"
    elif (place in ["神奈川", "千葉", "静岡"]):
        return "南関東"
    elif (place in ["石川", "富山", "岐阜", "愛知", "三重"]):
        return "中部"
    elif (place in ["福井", "滋賀", "京都", "大阪", "兵庫", "奈良", "和歌山"]):
        return "近畿"
    elif (place in ["岡山", "広島", "山口", "鳥取", "島根"]):
        return "中国"
    elif (place in ["香川", "徳島", "愛媛", "高知"]):
        return "四国"
    elif (place in ["福岡", "佐賀", "長崎", "熊本", "大分", "宮崎", "鹿児島", "沖縄"]):
        return "九州"
    else:
        return "出場なし"
    
def get_element_text(base_id, xpath):
    for retry in range(3):
        try:
            base = driver.find_element(By.ID, base_id)
            return base.find_element(By.XPATH, xpath).text
        except StaleElementReferenceException:
            if retry == 2:
                raise
            time.sleep(0.5)

def get_element_attribute(base_id, xpath, attribute):
    for retry in range(3):
        try:
            base = driver.find_element(By.ID, base_id)
            return base.find_element(By.XPATH, xpath).get_attribute(attribute)
        except StaleElementReferenceException:
            if retry == 2:
                raise
            time.sleep(0.5)

def click_element_by_id(id):
    for retry in range(3):
        try:
            el = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.ID, id))
            )
            print(el.get_attribute("outerHTML"))
            el.click()
        except StaleElementReferenceException:
            if retry == 2:
                raise
            time.sleep(0.5)

options = Options()
options.add_argument("--headless=new")  # ヘッドレスモードで実行

driver = webdriver.Chrome(options=options)
driver.get("https://keirin.jp/pc/raceschedule")
driver.implicitly_wait(3)

place_num = len(driver.find_elements(By.CLASS_NAME, "kyotuHeader"))
output = []
for p_num in range(place_num):
    place = driver.find_elements(By.CLASS_NAME, "kyotuHeader")[p_num]
    print(driver.find_elements(By.CLASS_NAME, "kyotuHeader")[p_num].get_attribute("outerHTML"))
    # ミッドナイト競輪以外では何もしない
    try:
        if place.find_element(By.CLASS_NAME, "HoldingIconSize").get_attribute("alt") != "5":
            print("ミッドナイト競輪ではないため、スキップします")
            print(place.find_element(By.CLASS_NAME, "HoldingIconSize").get_attribute("outerHTML"))
            continue
    except Exception as e:
        print("アイコンが見つかりませんでした")
        continue
    
    place_text = place.find_element(By.CLASS_NAME, "place").text
    print(f"{ place_text }をクリックしました")
    place.find_element(By.CLASS_NAME, "btn").click()
    
    print(f"{place_text}会場の情報を取得しています")
    time.sleep(5)

    date_num = len(driver.find_elements(By.NAME, "hhlnkRaceDate"))
    for d_num in range(date_num):
        d_id = f"hhlnkRaceDate{d_num}"
        
        # 日付の確認
        date_text = driver.find_element(By.ID, d_id).text
        today_text = time.strftime("%m/%d", time.localtime())

        # 今日の日付と異なれば何もしない
        if not date_text.startswith(today_text):
            continue
        
        # 今日の日付をクリック
        print(f"{date_text}をクリックしました")
        driver.execute_script("arguments[0].click();", driver.find_element(By.ID, d_id))

        # driver.find_element(By.ID, d_id).click()
        
        WebDriverWait(driver, 5).until(
            lambda d: "active" in driver.find_element(By.ID, d_id).find_element(By.XPATH, "..").get_attribute("class")
        )

        # 各レースのボタンを取得
        race_num = len(driver.find_elements(By.NAME, "hhRaceBtn"))
        
        for num in range(1, race_num + 1):
            race_id = f"hhRaceBtn{num}"
            race_text = driver.find_element(By.ID, race_id).text
            print(f"{race_text}をクリックしました")
            driver.execute_script("arguments[0].click();", driver.find_element(By.ID, race_id))
            # click_element_by_id(race_id)

            WebDriverWait(driver, 5).until(
                EC.text_to_be_present_in_element((By.ID, "hhLblRaceDtl"), race_text)
            )
            # print(driver.find_element(By.ID, "hhLblRaceDtl").text)

            dict = {}
            for i in range(1, 8):
                dict[f"{i}"] = {
                    "name": "出場なし",
                    "place": "出場なし",
                    "area": "出場なし",
                    "prev_class": "A3",
                    "cur_class": "A3",
                    "term": 999,
                    "age": 99,
                    "score": 0,
                    "breakaway": 0,
                    "sprinter": 0,
                    "finisher": 0,
                    "marker": 0,
                    "b": 0,
                    "h": 0,
                    "s": 0,
                    "win_rate": 0,
                    "top2": 0,
                    "top3": 0,
                    "prev1": 0,
                    "prev2": 0,
                    "prev3": 0,
                    "cur1": 0,
                    "cur2": 0,
                    "cur3": 0,
                }
                
                cur = dict[f"{i}"]
                
                try:
                    WebDriverWait(driver, 5).until(
                        EC.visibility_of_element_located((By.ID, f"rbLeftItem_{i}"))
                    )    
                except Exception as e:
                    # 選手情報がない場合は何もしない
                    print(f"選手情報が見つかりませんでした")
                    continue
                
                cur["name"] = get_element_text(f"rbLeftItem_{i}", "./td[4]/p[1]/span[1]/a").replace(" ", "").replace("　", "")
                # print(cur["name"])
                cur["place"] = get_element_text(f"rbLeftItem_{i}", "./td[4]/p[2]/span[1]").replace(" ", "").replace("　", "")
                # print(cur["place"])
                cur["area"] = get_area(cur["place"])
                # print(cur["area"])
                cur["prev_class"] = get_element_text(f"rbLeftItem_{i}", "./td[4]/p[2]/span[3]")
                # print(cur["prev_class"])
                cur["cur_class"] = get_element_text(f"rbLeftItem_{i}", "./td[4]/p[2]/span[4]")
                # print(cur["cur_class"])
                cur["term"] = int(get_element_text(f"rbLeftItem_{i}", "./td[5]/table/tbody/tr[1]/td/p/span"))
                # print(cur["term"])
                cur["age"] = int(get_element_text(f"rbLeftItem_{i}", "./td[5]/table/tbody/tr[2]/td/p/span"))
                # print(cur["age"])

                cur["score"] = float(get_element_text(f"rbRightItem_{i}_1", "./td[1]/p/span"))
                # print(cur["score"])
                cur["breakaway"] = int(get_element_text(f"rbRightItem_{i}_1", "./td[2]/table/tbody/tr/td[1]/p/span"))
                # print(cur["breakaway"])
                cur["sprinter"] = int(get_element_text(f"rbRightItem_{i}_1", "./td[2]/table/tbody/tr/td[2]/p/span"))
                # print(cur["sprinter"])
                cur["finisher"] = int(get_element_text(f"rbRightItem_{i}_1", "./td[2]/table/tbody/tr/td[3]/p/span"))
                # print(cur["finisher"])
                cur["marker"] = int(get_element_text(f"rbRightItem_{i}_1", "./td[2]/table/tbody/tr/td[4]/p/span"))
                # print(cur["marker"])
                cur["b"] = int(get_element_text(f"rbRightItem_{i}_1", "./td[3]/table/tbody/tr/td[1]/table/tbody/tr/td[1]/p/span"))
                # print(cur["b"])
                cur["h"] = int(get_element_text(f"rbRightItem_{i}_1", "./td[3]/table/tbody/tr/td[1]/table/tbody/tr/td[2]/p/span"))
                # print(cur["h"])
                cur["s"] = int(get_element_text(f"rbRightItem_{i}_1", "./td[3]/table/tbody/tr/td[2]/p/span"))
                # print(cur["s"])
                cur["win_rate"] = int(get_element_text(f"rbRightItem_{i}_1", "./td[4]/table/tbody/tr/td[1]/p/span"))
                # print(cur["win_rate"])
                cur["top2"] = int(get_element_text(f"rbRightItem_{i}_1", "./td[4]/table/tbody/tr/td[2]/p/span"))
                # print(cur["top2"])
                cur["top3"] = int(get_element_text(f"rbRightItem_{i}_1", "./td[4]/table/tbody/tr/td[3]/p/span"))
                # print(cur["top3"])

                for j in range(1, 4):
                    try:
                        style = get_element_attribute(f"rbRightItem_{i}_1", f"./td[6]/table/tbody/tr/td[{j}]/p", "style")
                        match = re.search(r"-(\d+)\.png", style)
                        if match:
                            cur[f"prev{j}"] = int(match.group(1))
                    except Exception as e:
                        try:
                            value = get_element_text(f"rbRightItem_{i}_1", f"./td[6]/table/tbody/tr/td[{j}]")
                            match = re.search(r"(\d+)", value)
                            if match:
                                cur[f"prev{j}"] = int(match.group(1))
                            else:
                                print(f"前走{j}の値が見つかりませんでした")
                                cur[f"prev{j}"] = 0
                        except Exception as e2:
                            print(f"前走情報が見つかりませんでした")
                            cur[f"prev{j}"] = 0

                    # print(cur[f"prev{j}"])
                    
                    if j <= 2:
                        try:
                            style = get_element_attribute(f"rbRightItem_{i}_2", f"./td[2]/table/tbody/tr/td[{j}]/p", "style")
                            match = re.search(r"-(\d+)\.png", style)
                            if match:
                                cur[f"cur{j}"] = int(match.group(1))
                        except Exception as e:
                            value = get_element_text(f"rbRightItem_{i}_2", f"./td[2]/table/tbody/tr/td[{j}]")
                            match = re.search(r"(\d+)", value)
                            if match:
                                cur[f"cur{j}"] = int(match.group(1))
                            else:
                                print(f"今走{j}が見つかりませんでした")
                                cur[f"cur{j}"] = 0
                        except Exception as e2:
                            print(f"今走情報が見つかりませんでした")
                            cur[f"cur{j}"] = 0
                                
                        # print(cur[f"cur{j}"])
                         
            columns = [
                "name",
                "place",
                "area",
                "prev_class",
                "cur_class",
                "term",
                "age",
                "score",
                "breakaway",
                "sprinter",
                "finisher",
                "marker",
                "b",
                "h",
                "s",
                "win_rate",
                "top2",
                "top3",
                "prev1",
                "prev2",
                "prev3",
                "cur1",
                "cur2",
            ]
            
            for i in range(1, 8):
                row = [
                    time.strftime("%Y/%m/%d", time.localtime()),
                    place_text,
                    get_place_prefecture(place_text),
                    "通常",
                    i
                ]
                for col in columns:
                    row.append(dict[f"{i}"][col])
                    
                output.append(row)
    
# --- 環境切り替え（環境変数 ENV="stable" or "dev"）---
ENV = os.getenv("ENV", "dev")

# --- パス設定 ---
if getattr(sys, 'frozen', False):
    # 実行ファイル時
    BASE_DIR = Path(sys.executable).parent
    while BASE_DIR.name != "stable":
        BASE_DIR = BASE_DIR.parent
    BASE_DIR = BASE_DIR.parent
    RESOURCE_DIR = Path(sys._MEIPASS) / ENV
else:
    # 開発環境（スクリプト直実行）
    BASE_DIR = Path(__file__).resolve()
    while BASE_DIR.name != "keirin_predictor":
        BASE_DIR = BASE_DIR.parent
    RESOURCE_DIR = BASE_DIR / ENV

# --- 書き込み系ディレクトリ設定 ---
ENV_DIR = BASE_DIR / ENV
DATA_DIR = ENV_DIR / "data"

# 必要に応じて出力先ディレクトリを作成
DATA_DIR.mkdir(parents=True, exist_ok=True)

# --- ファイルパス指定 ---
OUTPUT_PATH = DATA_DIR / "predict_data.tsv"

with open(OUTPUT_PATH, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f, delimiter="\t")
    writer.writerows(output)
    print(f"データを {OUTPUT_PATH} に保存しました。")

driver.quit()