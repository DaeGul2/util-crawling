from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd

# 크롬드라이버 실행 경로 설정
driver_path = "C:/chromedriver-win64/chromedriver.exe"
service = Service(executable_path=driver_path)
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")  # 창 최대화
driver = webdriver.Chrome(service=service, options=options)

# 크롤링할 네이버 브랜드 스토어 상품 리뷰 페이지
url = "https://brand.naver.com/sanmoae/products/5592524686#REVIEW"
driver.get(url)

# 웹페이지가 완전히 로드되도록 대기
time.sleep(3)

# ✅ 사용자가 "Enter" 키를 눌러야 크롤링 시작
input("🔴 리뷰 크롤링을 시작하려면 Enter를 누르세요...")

# ✅ 크롤링할 데이터 저장 리스트
reviews = []

# ✅ 최대 페이지 설정
MAX_PAGES = 30  
current_page = 1  

while current_page <= MAX_PAGES:
    print(f"🔍 {current_page} 페이지 크롤링 중...")

    try:
        # 리뷰 리스트 가져오기 (XPath 활용)
        review_elements = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located(
                (By.XPATH, "//div[contains(@class, 'review') or contains(@class, '_9oeeh3ukt7')]")
            )
        )
    except:
        print("🚫 리뷰 로딩 실패")
        break

    for review in review_elements:
        try:
            username = review.find_element(By.XPATH, ".//strong[contains(@class, '_2L3vDiadT9')]").text
            date = review.find_element(By.XPATH, ".//span[contains(@class, '_2L3vDiadT9')]").text
            rating = review.find_element(By.XPATH, ".//em[contains(@class, '_15NU42F3kT')]").text
            
            # ✅ 리뷰 텍스트 크롤링 (리뷰 본문에 해당하는 부분 찾기)
            content_elements = review.find_elements(By.XPATH, ".//span[contains(@class, '_2L3vDiadT9')]")
            content = ""
            for element in content_elements:
                text = element.text.strip()
                if text and "신고" not in text:  # 신고 버튼 같은 불필요한 텍스트 필터링
                    content = text
                    break

            reviews.append([username, date, rating, content])
            print(f"✅ {username} | {date} | 평점: {rating}\n{content}\n\n" + "-" * 60)
        except Exception as e:
            print(f"❌ 리뷰 추출 오류: {e}")

    # ✅ 페이지네이션 로직 (2~10 클릭 후 '다음' 버튼 클릭)
    if current_page % 10 != 0:  # 1~9, 11~19, 21~29에서는 숫자 버튼 클릭
        try:
            next_page_button = driver.find_element(By.XPATH, f"//a[text()='{current_page + 1}']")
            driver.execute_script("arguments[0].click();", next_page_button)
            time.sleep(3)
            current_page += 1
            continue
        except:
            print(f"🚫 {current_page+1} 페이지 버튼을 찾을 수 없음.")
            break
    else:  # 10, 20, 30 페이지 후에는 '다음' 버튼 클릭
        try:
            next_button = driver.find_element(By.XPATH, "//a[contains(text(), '다음')]")
            driver.execute_script("arguments[0].click();", next_button)
            time.sleep(3)
            current_page += 1
        except:
            print("🚫 '다음' 버튼을 찾을 수 없음. 크롤링 종료.")
            break

# ✅ 크롤링 완료 후 WebDriver 종료
driver.quit()

# ✅ 데이터 CSV 파일 저장
df = pd.DataFrame(reviews, columns=["작성자", "날짜", "평점", "리뷰"])
df.to_csv("naver_reviews.csv", index=False, encoding="utf-8-sig")
print("✅ 크롤링 완료! 데이터 저장됨: `naver_reviews.csv`")
