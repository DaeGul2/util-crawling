import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup

def parse_content(divs):
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

        try:
            now_box = div.find('div', class_='now_box')
            dl_now = now_box.find('dl')
            dd_now = dl_now.find_all('dd', class_='txt_img')
            interview_result = dd_now[0].get_text(strip=True) if len(dd_now) > 0 else ''
            interview_experience = dd_now[1].get_text(strip=True) if len(dd_now) > 1 else ''
        except:
            interview_result = interview_experience = ''

        parsed_data.append([idx, interview_text, interview_question, interview_answer,
                            recruitment_method, announcement_timing, interview_result, interview_experience])
    return parsed_data

# 크롬 드라이버 설정
driver_path = "C:/chromedriver-win64/chromedriver.exe"
service = Service(executable_path=driver_path)
driver = webdriver.Chrome(service=service)

parsed_data = []
print("Type 'quit' to exit or press any other key to continue:")
command = input().lower()
if command == 'quit':
    driver.quit()
    exit()

target_url = "https://www.jobplanet.co.kr/companies/87779/interviews/%EB%8C%80%EA%B5%AC%EA%B5%90%ED%86%B5%EA%B3%B5%EC%82%AC"

# 페이지 파싱 시작
page = 1
while True:
    url = f"{target_url}?page={page}"
    driver.get(url)
    time.sleep(2)  # 페이지 로드 대기

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    content_divs = soup.find_all('div', class_='content_body_ty1')

    if len(content_divs) < 1:
        print("No more interviews to parse. Exiting...")
        break

    # 인터뷰 데이터 파싱
    new_data = parse_content(content_divs)
    parsed_data.extend(new_data)
    print(f"Page {page} parsed and added to data.")
    page += 1

# 엑셀로 저장
output_file = 'output_data.xlsx'
columns = ["번호", "인터뷰 내용", "면접 질문", "면접 답변", "채용 방식", "발표 시기", "면접 결과", "면접 경험"]
output_df = pd.DataFrame(parsed_data, columns=columns)
output_df.to_excel(output_file, index=False)
print(f"Data saved to {output_file}")

driver.quit()
