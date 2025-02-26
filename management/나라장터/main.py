from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

# 크롬 드라이버 설정 (자동 설치)
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

# G2B 사이트 열기
url = "https://www.g2b.go.kr/"
driver.get(url)
print(f"\n✅ G2B 사이트({url})가 열렸습니다.")

# 찾을 텍스트
target_text = "2025년도 직원 채용 위탁"

def wait_for_next():
    while True:
        command = input("\n⏭️ 'next' 입력 시 다음 단계 진행: ").strip().lower()
        if command == "next":
            break
        else:
            print("⚠️ 올바른 명령어를 입력하세요 ('next').")

def click_target_link():
    try:
        print(f"\n🔍 '{target_text}'을(를) 찾는 중...")
        wait_for_next()
        
        attempts = 0
        while attempts < 20:
            try:
                link_element = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, f"//a[contains(text(), '{target_text}')]"))
                )
                link_element.click()
                print(f"✅ '{target_text}' 클릭 완료!")
                break
            except:
                attempts += 1
                print(f"🔻 타겟 찾기 실패, 스크롤 조금씩 내림 (시도 {attempts})")
                driver.execute_script("window.scrollBy(0, 800);")
                time.sleep(1)
        
        wait_for_next()
        
        bid_opening_link = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//a[span[text()='개찰(조달업체)']]"))
        )
        bid_opening_link.click()
        print("✅ 개찰(조달업체) 클릭 완료!")
        time.sleep(3)
        
        wait_for_next()
        
        bid_complete_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), '개찰완료')]"))
        )
        bid_complete_button.click()
        print("✅ 개찰완료 버튼 클릭 완료!")
        time.sleep(3)
        
        wait_for_next()
        
        bid_table = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//table[contains(@class, 'gridHeaderTableDefault')]"))
        )
        print(bid_table)
        tbody = bid_table.find_element(By.TAG_NAME, "tbody")
        print(tbody)
        rows = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, "//table[contains(@class, 'gridHeaderTableDefault')]//tr"))
        )

        
        if not rows:
            print("❌ [오류] 테이블 행을 찾을 수 없습니다.")
            return
        
        for i, row in enumerate(rows):
            print(f"\n🔍 [{i+1}번째 행] 데이터 추출 중...")
            wait_for_next()
            
            business_number = row.find_element(By.XPATH, "./td[2]/a")
            business_number.click()
            print("✅ 사업자등록번호 클릭 완료!")
            time.sleep(2)
            
            wait_for_next()
            
            bid_price_score = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//input[@title='입찰가격점수']"))
            ).get_attribute("value")
            
            tech_eval_score = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//input[@title='기술평가점수']"))
            ).get_attribute("value")
            
            print(f"🏆 입찰가격점수: {bid_price_score}, 기술평가점수: {tech_eval_score}")
            
            wait_for_next()
            
            close_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//input[@value='닫기']"))
            )
            close_button.click()
            time.sleep(2)
            
            wait_for_next()
            
            company_name = row.find_element(By.XPATH, "./td[3]").text
            bid_amount = row.find_element(By.XPATH, "./td[5]").text
            bid_rate = row.find_element(By.XPATH, "./td[6]").text
            
            print(f"🏢 업체명: {company_name}, 💵 입찰금액: {bid_amount}, 📊 투찰률: {bid_rate}")
            
    except Exception as e:
        print(f"❌ [오류] 처리 실패: {str(e)}")

while True:
    command = input("\n📝 명령을 입력하세요 ('start' 입력 시 검색 및 클릭 / 'quit' 입력 시 종료): ").strip().lower()
    if command == "start":
        click_target_link()
    elif command == "quit":
        print("🔻 브라우저를 종료합니다.")
        break
    else:
        print("⚠️ 올바른 명령어를 입력하세요 ('start' 또는 'quit').")

driver.quit()
print("✅ 프로그램이 종료되었습니다.")
