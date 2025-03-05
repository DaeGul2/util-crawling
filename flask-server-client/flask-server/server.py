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
from bs4 import BeautifulSoup

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
    output_file = "merged_review.xlsx"
    columns = ["번호", "인터뷰 내용", "면접 질문", "면접 답변", "채용 방식", "발표 시기"]  # 6개로 수정

    output_df = pd.DataFrame(parsed_data, columns=columns)
    output_df.to_excel(output_file, index=False)
    print(f"Data saved to {output_file}")

    # '인터뷰 내용'과 '면접 답변' 컬럼을 합쳐 새로운 컬럼 생성
    data = pd.read_excel(output_file)
    data['review'] = '응답자의 한줄평 : ' + data['인터뷰 내용'].astype(str) + '\n응답자의 면접느낀점 : ' + data['면접 답변'].astype(str)

    # 결과를 새로운 엑셀 파일로 저장
    data.to_excel(output_file, index=False)
    print(f"Updated data saved to {output_file}")

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
@app.route('/start-naver-price', methods=['GET'])
def start_naver_price_browser():
    """ 네이버 가격 리뷰 크롤링 브라우저 실행 """
    global driver
    if driver is None:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)

    driver.get("https://shopping.naver.com/home")  # 네이버 쇼핑 홈으로 이동
    return jsonify({"message": "브라우저가 실행되었습니다. 원하는 상품 페이지로 이동 후 '크롤링 시작' 버튼을 눌러주세요."})


@app.route('/naver-price-crawl', methods=['POST'])
def naver_price_crawl():
    """ 네이버 가격 리뷰 크롤링 시작 (사용자가 직접 페이지 이동 후 실행) """
    global driver
    if driver is None:
        return jsonify({"message": "먼저 브라우저를 실행하세요."})

    data = request.json
    max_pages = int(data.get("max_pages", 10))  # 기본 10페이지

    parsed_data = []
    current_page = 1

    while current_page <= max_pages:
        print(f"🔍 {current_page} 페이지 크롤링 중...")

        try:
            # 광고 제외한 상품 리스트 가져오기
            product_elements = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, 'product_item__MDtDF')]"))
            )
        except:
            print("🚫 상품 목록 로딩 실패")
            break

        for product in product_elements:
            try:
                # 광고 제품 필터링
                is_ad = (
                    len(product.find_elements(By.XPATH, ".//svg[contains(@class, 'svg_ad')]")) > 0
                    or "superSavingProduct_" in product.get_attribute("class")
                )
                if is_ad:
                    continue
                
                # 쇼핑몰명 봤을 때, 쿠팡이나 그런 잔바리면 재낌낌
                try:
                    shop_name_element = product.find_element(By.XPATH, ".//a[contains(@class, 'product_mall')]")
                    shop_name = shop_name_element.text.strip()

                    # ✅ 쇼핑몰 이름이 빈 문자열이면 이미지의 alt 속성에서 가져오기
                    if not shop_name:
                        continue
                        
                except:
                    shop_name = "정보 없음"
                # 상품명
                product_name = product.find_element(By.XPATH, ".//div[contains(@class, 'product_title')]/a").text
                
                # 가격
                price = product.find_element(By.XPATH, ".//span[contains(@class, 'price_num')]").text.replace(",", "")
                
                
                try:
                # ✅ 리뷰 수 & 찜 수를 포함하는 전체 텍스트 가져오기
                    etc_box = product.find_element(By.CLASS_NAME, "product_etc_box__ElfVA").text

                    # ✅ 리뷰 수 정규식으로 추출 (ex: "(3만)" 또는 "(244)")
                    review_match = re.search(r"\(([\d,]+(?:\.\d+)?[만]?)\)", etc_box)
                    if review_match:
                        review_count = review_match.group(1)
                        # "3만" 같은 경우 "30000" 으로 변환
                        if "만" in review_count:
                            review_count = review_count.replace("만", "")
                            review_count = str(int(float(review_count) * 10000))
                    else:
                        review_count = "0"  # 리뷰 없음

                    # ✅ 찜 수 정규식으로 추출 (ex: "찜 1,463")
                    jjim_match = re.search(r"찜\s([\d,]+)", etc_box)
                    if jjim_match:
                        jjim_count = jjim_match.group(1).replace(",", "")
                    else:
                        jjim_count = "0"  # 찜 없음

                except:
                    review_count = "0"
                    jjim_count = "0"
                # ✅ 용량 (우선 태그에서 찾고, 없으면 제품명에서 정규식으로 추출)
                try:
                    capacity_element = driver.find_element(By.XPATH, "//a[contains(@data-shp-contents-type, '용량_M')]")
                    capacity = capacity_element.text.replace("용량 : ", "").strip()
                except:
                    # 제품명에서 정규식으로 용량 추출
                    import re
                    match = re.search(r'(\d+(?:\.\d+)?)(ml|g|l|kg)', product_name.lower().replace(" ", ""))
                    capacity = match.group(0) if match else "정보 없음"

                # 구매 수
                try:
                    purchase_count = product.find_element(By.XPATH, ".//span[contains(text(), '구매')]/em").text
                except:
                    purchase_count = "0"

                # 등록일
                try:
                    reg_date = product.find_element(By.XPATH, ".//span[contains(text(), '등록일')]").text.replace("등록일 ", "")
                except:
                    reg_date = "정보 없음"

                
                try:
                    delivery_element = product.find_element(By.CLASS_NAME, "price_delivery__yw_We")
                    delivery_text = delivery_element.text.strip()

                    # 숫자 + 원 또는 "무료" 만 추출
                    delivery_match = re.search(r"(\d{1,3}(,\d{3})*원|무료)", delivery_text)
                    delivery_fee = delivery_match.group(1) if delivery_match else "0원"

                except:
                    delivery_fee = "0원"  # 기본값 설정


                # ✅ 종류, 효과, 특징, 포장형태 추출
                try:
                    desc_elements = product.find_elements(By.XPATH, ".//div[contains(@class, 'product_desc__m2mVJ')]/div/a")
                    product_type, effects, features, packaging = "", [], [], []

                    for desc in desc_elements:
                        desc_text = desc.text
                        if "종류 :" in desc_text:
                            product_type = desc_text.replace("종류 :", "").strip()
                        elif "효과 :" in desc_text or "효과" in desc_text:
                            effects.append(desc_text.replace("효과 :", "").strip())
                        elif "특징 :" in desc_text or "특징" in desc_text:
                            features.append(desc_text.replace("특징 :", "").strip())
                        elif "포장형태 :" in desc_text or "포장형태" in desc_text:
                            packaging.append(desc_text.replace("포장형태 :", "").strip())

                    effects_text = ", ".join(effects) if effects else "정보 없음"
                    features_text = ", ".join(features) if features else "정보 없음"
                    packaging_text = ", ".join(packaging) if packaging else "정보 없음"

                except:
                    product_type, effects_text, features_text, packaging_text = "정보 없음", "정보 없음", "정보 없음", "정보 없음"

                # ✅ 카테고리 Depth (최대 4개)
                try:
                    category_elements = product.find_elements(By.XPATH, ".//div[contains(@class, 'product_depth__I4SqY')]/span")
                    categories = [cat.text for cat in category_elements]
                    depth1 = categories[0] if len(categories) > 0 else "정보 없음"
                    depth2 = categories[1] if len(categories) > 1 else "정보 없음"
                    depth3 = categories[2] if len(categories) > 2 else "정보 없음"
                    depth4 = categories[3] if len(categories) > 3 else "정보 없음"
                except:
                    depth1, depth2, depth3, depth4 = "정보 없음", "정보 없음", "정보 없음", "정보 없음"

                # 결과 리스트에 추가
                parsed_data.append([product_name, price, capacity,review_count,  purchase_count, reg_date,delivery_fee ,shop_name,
                                    product_type, effects_text, features_text, packaging_text, depth1, depth2, depth3, depth4])

                print(f"✅ {product_name} | {price}원 | 리뷰: {review_count} | 찜: {jjim_count} | 구매: {purchase_count} | {shop_name}")
                print(f"   카테고리: {depth1} > {depth2} > {depth3} > {depth4}")
                print(f"   종류: {product_type} | 효과: {effects_text} | 특징: {features_text} | 포장형태: {packaging_text}")

            except Exception as e:
                print(f"❌ 상품 데이터 추출 오류: {e}")

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
    output_file = "naver_price.xlsx"
    columns = ["상품명", "가격","용량" ,"리뷰 수",  "구매 수", "등록일","배송비", "쇼핑핑몰명", "종류", "효과", "특징", "포장형태", "Depth1", "Depth2", "Depth3", "Depth4"]
    output_df = pd.DataFrame(parsed_data, columns=columns)
    output_df.to_excel(output_file, index=False)
    print(f"✅ 크롤링 완료! 데이터 저장됨: `{output_file}`")

    return jsonify({"message": "크롤링 완료", "download_url": f"http://localhost:5000/download/{output_file}"})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
