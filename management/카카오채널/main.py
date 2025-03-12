from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import pandas as pd

# 크롬드라이버 자동 다운로드 및 실행
chrome_options = Options()
chrome_options.add_argument("--start-maximized")  # 창 최대화
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option("useAutomationExtension", False)

service = Service(ChromeDriverManager().install())  # 최신 크롬드라이버 자동 설치
driver = webdriver.Chrome(service=service, options=chrome_options)

# 카카오 채널 1:1 채팅 페이지 열기
driver.get("https://center-pf.kakao.com/")  # 해당 URL 직접 접속 후 로그인 필요
print("✅ 크롬 드라이버 실행 완료. 카카오 채널로 직접 이동하세요.")
input("➡️ 로그인 후 채팅 목록 페이지에서 'Enter'를 누르세요: ")

# 스크롤 및 데이터 수집 시작 대기
print("⏳ 터미널에 'start' 입력하면 크롤링을 시작합니다.")
while True:
    command = input("입력: ")
    if command.lower() == "start":
        print("🚀 크롤링 시작!")
        break

# 데이터 저장 리스트 (중복 방지를 위한 집합 활용)
collected_chats = set()
chat_data = []
previous_top_values = set()  # li의 top 값 추적

while True:
    # 현재 HTML 가져와서 파싱
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, "html.parser")

    chat_items = soup.find_all("li")
    last_top_value = None  # 현재 스크롤에서 마지막 li의 top 값을 저장

    for chat in chat_items:
        style_attr = chat.get("style", "")
        top_value = None

        # `top:` 값 추출
        for style in style_attr.split(";"):
            if "top:" in style:
                top_value = int(style.split(":")[1].strip().replace("px", ""))
                last_top_value = top_value  # 현재 마지막 top 값 저장

        name_span = chat.find("span", class_="txt_name")
        date_span = chat.find("span", class_="txt_date")
        msg_span = chat.find("p", class_="txt_info")
        img_tag = chat.find("img")

        if name_span and date_span and msg_span and img_tag and top_value is not None:
            name = name_span.text.strip()
            date = date_span.text.strip()
            msg = msg_span.text.strip()
            img_src = img_tag["src"]

            chat_tuple = (name, msg, date, img_src, top_value)

            # 중복되지 않은 경우 추가
            if chat_tuple not in collected_chats:
                collected_chats.add(chat_tuple)
                chat_data.append({
                    "이름": name,
                    "메시지": msg,
                    "최근 연락일": date,
                    "이미지 URL": img_src
                })

    # 마지막 top 값이 이전에 나왔던 값이면 종료
    if last_top_value in previous_top_values:
        print("✅ 크롤링 완료! 더 이상 새로운 데이터가 없습니다.")
        break
    previous_top_values.add(last_top_value)  # 새로운 top 값 추가

    # 사용자에게 스크롤 요청
    input("⏳ 스크롤을 수동으로 내린 후 'Enter'를 누르세요...")

# 웹드라이버 종료
driver.quit()

# 데이터를 DataFrame으로 변환 후 엑셀 저장
df = pd.DataFrame(chat_data)
df.to_excel("카카오_채팅목록.xlsx", index=False)

print("✅ 데이터 수집 완료. '카카오_채팅목록.xlsx' 파일로 저장됨.")
