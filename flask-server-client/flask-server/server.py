from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import time
import pandas as pd
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import re

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

app = Flask(__name__)
CORS(app)  # CORS 허용

# 크롬 드라이버 설정
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")  # 브라우저 최대화
driver = None  # 전역 변수

@app.route('/start', methods=['GET'])
def start_browser():
    """ 브라우저 실행 (로그인용) """
    global driver
    if driver is None:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)

    driver.get("https://www.jobplanet.co.kr/users/sign_in")
    return jsonify({"message": "브라우저 실행 완료. 로그인 후 '크롤링 시작' 버튼을 눌러주세요."})

@app.route('/crawl', methods=['POST'])
def crawl():
    """ 로그인 후 크롤링 시작 """
    global driver
    if driver is None:
        return jsonify({"message": "먼저 브라우저를 실행하세요."})

    data = request.json
    target_url = data.get("target_url")

    if not target_url:
        return jsonify({"message": "크롤링할 URL이 필요합니다."})

    parsed_data = []
    page = 1

    while True:
        url = f"{target_url}?page={page}"
        driver.get(url)
        time.sleep(2)

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        content_divs = soup.find_all('div', class_='content_body_ty1')

        if len(content_divs) < 1:
            break

        new_data = parse_content(content_divs)
        parsed_data.extend(new_data)
        print(f"Page {page} parsed and added to data.")
        page += 1

    # 엑셀로 저장
    output_file = "interviews.xlsx"
    columns = ["번호", "인터뷰 내용", "면접 질문", "면접 답변", "채용 방식", "발표 시기"]  # 6개로 수정

    output_df = pd.DataFrame(parsed_data, columns=columns)
    output_df.to_excel(output_file, index=False)
    print(f"Data saved to {output_file}")

    # ✅ 파일 다운로드 URL을 클라이언트에 반환
    return jsonify({"message": "크롤링 완료", "download_url": f"http://localhost:5000/download/{output_file}"})

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    """ 클라이언트에서 파일을 다운로드할 수 있도록 제공 """
    file_path = os.path.join(os.getcwd(), filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return jsonify({"message": "파일을 찾을 수 없습니다."}), 404

def parse_content(divs):
    """ BeautifulSoup으로 페이지 내용 파싱 """
    parsed_data = []
    for idx, div in enumerate(divs, start=1):
        try:
            interview_text = div.find('div', class_='us_label_wrap').find('h2', class_='us_label').get_text(strip=True)
        except:
            interview_text = ''

        try:
            tc_list = div.find('dl', class_='tc_list')
            dd_tags = tc_list.find_all('dd', class_='df1')
            interview_question = dd_tags[0].get_text(separator=" ", strip=True) if len(dd_tags) > 0 else ''
            interview_answer = dd_tags[1].get_text(separator=" ", strip=True) if len(dd_tags) > 1 else ''
            recruitment_method = dd_tags[2].get_text(separator=" ", strip=True) if len(dd_tags) > 2 else ''
            announcement_timing = dd_tags[3].get_text(separator=" ", strip=True) if len(dd_tags) > 3 else ''
        except:
            interview_question = interview_answer = recruitment_method = announcement_timing = ''

        parsed_data.append([idx, interview_text, interview_question, interview_answer,
                            recruitment_method, announcement_timing])
    return parsed_data
@app.route('/start-naver', methods=['GET'])
def start_naver_browser():
    """ 네이버 쇼핑몰 브라우저 실행 """
    global driver
    if driver is None:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)

    driver.get("https://shopping.naver.com/home")  # 네이버 쇼핑 홈으로 이동
    return jsonify({"message": "브라우저가 실행되었습니다. 원하는 상품 페이지로 이동 후 '크롤링 시작' 버튼을 눌러주세요."})

@app.route('/naver-crawl', methods=['POST'])
def naver_crawl():
    """ 네이버 쇼핑 리뷰 크롤링 시작 """
    global driver
    if driver is None:
        return jsonify({"message": "먼저 브라우저를 실행하세요."})

    data = request.json
    max_pages = int(data.get("max_pages", 10))  # 기본값 10페이지

    parsed_data = []
    current_page = 1  

    while current_page <= max_pages:
        print(f"🔍 {current_page} 페이지 크롤링 중...")

        try:
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
                
                raw_html = review.get_attribute('innerHTML')
                review_content = extract_review_text(raw_html)

                parsed_data.append([username, date, rating, review_content])
                print(f"✅ {username} | {date} | 평점: {rating}\n{review_content}\n\n" + "-" * 60)
            except Exception as e:
                print(f"❌ 리뷰 추출 오류: {e}")

        # ✅ 페이지네이션 로직
        if current_page % 10 != 0:
            try:
                next_page_button = driver.find_element(By.XPATH, f"//a[text()='{current_page + 1}']")
                driver.execute_script("arguments[0].click();", next_page_button)
                time.sleep(3)
                current_page += 1
                continue
            except:
                print(f"🚫 {current_page+1} 페이지 버튼을 찾을 수 없음.")
                break
        else:
            try:
                next_button = driver.find_element(By.XPATH, "//a[contains(text(), '다음')]")
                driver.execute_script("arguments[0].click();", next_button)
                time.sleep(3)
                current_page += 1
            except:
                print("🚫 '다음' 버튼을 찾을 수 없음. 크롤링 종료.")
                break

    # ✅ 엑셀 파일 저장
    output_file = "naver_reviews.xlsx"
    columns = ["작성자", "날짜", "평점", "리뷰"]
    output_df = pd.DataFrame(parsed_data, columns=columns)
    output_df.to_excel(output_file, index=False)
    print(f"✅ 크롤링 완료! 데이터 저장됨: `{output_file}`")

    return jsonify({"message": "크롤링 완료", "download_url": f"http://localhost:5000/download/{output_file}"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
