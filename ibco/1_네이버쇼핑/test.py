from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
import re

# ✅ 크롬드라이버 실행 경로 설정
driver_path = "C:/chromedriver-win64/chromedriver.exe"
service = Service(executable_path=driver_path)
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")  # 창 최대화
driver = webdriver.Chrome(service=service, options=options)

# ✅ 크롤링할 네이버 브랜드 스토어 상품 리뷰 페이지
url = "https://brand.naver.com/sanmoae/products/5592524686#REVIEW"
driver.get(url)

# ✅ 웹페이지가 완전히 로드되도록 대기
time.sleep(3)

# ✅ 사용자가 "Enter" 키를 눌러야 크롤링 시작
input("🔴 리뷰 크롤링을 시작하려면 Enter를 누르세요...")

# ✅ 크롤링할 데이터 저장 리스트
reviews = []

# ✅ 최대 페이지 설정
MAX_PAGES = 30  
current_page = 1  

# ✅ 리뷰 본문 정제 함수 (불필요한 정보 & 이미지 제거)
def extract_review_text(raw_html):
    """
    HTML에서 리뷰 본문만 추출하는 함수 (이미지 태그 제거 포함)
    """
    # ✅ <span> 태그 중 <img>를 포함한 태그 제거
    raw_html = re.sub(r'<span[^>]*><img.*?></span>', '', raw_html, flags=re.DOTALL)

    # ✅ <span> 태그 안의 텍스트 추출
    review_texts = re.findall(r'<span[^>]*>(.*?)</span>', raw_html, re.DOTALL)

    # ✅ 불필요한 키워드 제거
    exclude_keywords = ["평점", "신고", "이미지 펼쳐보기", "더보기", "리뷰 더보기/접기", "사진/비디오 수", "스토어PICK", "한달사용"]

    clean_texts = []
    for text in review_texts:
        text = text.strip()
        if not any(keyword in text for keyword in exclude_keywords):
            clean_texts.append(text)

    # ✅ 정제된 텍스트 반환 (여러 줄을 하나로 합침)
    return " ".join(clean_texts)

# ✅ 크롤링 루프 시작
while current_page <= MAX_PAGES:
    print(f"🔍 {current_page} 페이지 크롤링 중...")

    try:
        # ✅ 리뷰 리스트 가져오기 (li 태그 기준으로 전체 요소 가져오기)
        review_elements = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, "//li[contains(@class, 'BnwL_cs1av')]"))
        )
    except:
        print("🚫 리뷰 로딩 실패")
        break

    for review in review_elements:
        try:
            username = review.find_element(By.XPATH, ".//strong[contains(@class, '_2L3vDiadT9')]").text
            date = review.find_element(By.XPATH, ".//span[contains(@class, '_2L3vDiadT9')]").text
            rating = review.find_element(By.XPATH, ".//em[contains(@class, '_15NU42F3kT')]").text
            
            # ✅ 리뷰 텍스트 전체 가져오기
            raw_html = review.get_attribute('innerHTML')
            review_content = extract_review_text(raw_html)

            # ✅ 데이터 저장
            reviews.append([username, date, rating, review_content])
            print(f"✅ {username} | {date} | 평점: {rating}\n{review_content}\n\n" + "-" * 60)
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

# ✅ 데이터 Excel 파일 저장
df = pd.DataFrame(reviews, columns=["작성자", "날짜", "평점", "리뷰"])
excel_filename = "naver_reviews.xlsx"

# ✅ `encoding="utf-8-sig"` 제거 → XlsxWriter 엔진 사용하여 저장
df.to_excel(excel_filename, index=False, engine="xlsxwriter")

print(f"✅ 크롤링 완료! 데이터 저장됨: `{excel_filename}`")
