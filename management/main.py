import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

# 크롬 드라이버 설정
driver_path = "C:/chromedriver-win64/chromedriver.exe"
service = Service(executable_path=driver_path)
driver = webdriver.Chrome(service=service)

# G2B 사이트 열기
url = "https://www.g2b.go.kr/"
driver.get(url)
print(f"\n✅ G2B 사이트({url})가 열렸습니다.")

# 기본 날짜 설정
start_date = "2025.01.01"
end_date = "2025.02.25"

# 페이지 소스에서 정규식으로 input 태그 찾기
def get_dynamic_input_ids():
    print("\n🔍 [디버깅] 페이지 소스에서 input 태그 찾기 시작...")
    page_source = driver.page_source  # 현재 HTML 소스 가져오기
    soup = BeautifulSoup(page_source, 'html.parser')

    # 시작일 input 찾기
    start_input_tag = soup.find("input", {
        "title": re.compile(r"시작 날짜를 선택하세요"), 
        "class": re.compile(r"w2input.*?udcDateReadOnly")
    })
    
    # 종료일 input 찾기
    end_input_tag = soup.find("input", {
        "title": re.compile(r"종료 날짜를 선택하세요"), 
        "class": re.compile(r"w2input.*?udcDateReadOnly")
    })

    # 결과 확인 (디버깅)
    if start_input_tag:
        print(f"✅ [디버깅] 시작일 input 태그 찾음: {start_input_tag}")
    else:
        print("❌ [디버깅] 시작일 input 태그를 찾지 못함!")

    if end_input_tag:
        print(f"✅ [디버깅] 종료일 input 태그 찾음: {end_input_tag}")
    else:
        print("❌ [디버깅] 종료일 input 태그를 찾지 못함!")

    # id 추출
    start_input_id = start_input_tag.get("id") if start_input_tag else None
    end_input_id = end_input_tag.get("id") if end_input_tag else None
    
    return start_input_id, end_input_id

# 날짜 입력 함수 (JavaScript 활용)
def input_date(date, is_start=True):
    print(f"\n🔍 [디버깅] {'시작' if is_start else '종료'} 날짜 입력 시도: {date}")

    try:
        # 동적으로 id 찾기
        start_input_id, end_input_id = get_dynamic_input_ids()
        input_id = start_input_id if is_start else end_input_id

        if not input_id:
            print(f"❌ [오류] {'시작' if is_start else '종료'} 날짜 입력 필드를 찾을 수 없습니다.")
            return
        
        # 입력 필드 찾기
        print(f"🔍 [디버깅] 찾은 input 필드 ID: {input_id}")
        
        date_input = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, input_id))
        )
        
        print(f"✅ [디버깅] input 필드 찾음, 날짜 입력 시도...")

        # JavaScript로 값 설정 (readOnly 우회)
        driver.execute_script(f'document.getElementById("{input_id}").value = "{date}";')

        # 입력 필드 클릭 후 TAB 키 입력 (UI 반영)
        date_input.click()
        date_input.send_keys(Keys.TAB)

        print(f"✅ {'시작' if is_start else '종료'} 날짜를 {date}로 입력 완료!")

    except Exception as e:
        print(f"❌ [오류] 날짜 입력 중 예외 발생: {str(e)}")

while True:
    command = input("\n📝 명령을 입력하세요 ('start' 입력 시 날짜 입력 / 'quit' 입력 시 종료): ").strip().lower()
    
    if command == "start":
        try:
            input_date(start_date, is_start=True)
            input_date(end_date, is_start=False)
        except Exception as e:
            print(f"❌ [오류] 날짜 입력 중 오류 발생: {str(e)}")

    elif command == "quit":
        print("🔻 브라우저를 종료합니다.")
        break
    
    else:
        print("⚠️ 올바른 명령어를 입력하세요 ('start' 또는 'quit').")

# 크롬 종료
driver.quit()
print("✅ 프로그램이 종료되었습니다.")
