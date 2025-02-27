from flask import Flask, request, jsonify
from flask_cors import CORS
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager

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
    output_file = 'interviews.xlsx'
    columns = ["번호", "인터뷰 내용", "면접 질문", "면접 답변", "채용 방식", "발표 시기"]  # 6개로 수정

    output_df = pd.DataFrame(parsed_data, columns=columns)
    output_df.to_excel(output_file, index=False)
    print(f"Data saved to {output_file}")

    return jsonify({"message": "크롤링 완료", "file": output_file})

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
