import pandas as pd

# 파일을 로드하기
file_path = '한국전기안전공단_리뷰.xlsx'
data = pd.read_excel(file_path)

# '인터뷰 내용'과 '면접 답변' 컬럼을 합쳐 새로운 컬럼 생성
data['review'] = '응답자의 한줄평 : ' + data['인터뷰 내용'].astype(str) + '\n응답자의 면접느낀점 : ' + data['면접 답변'].astype(str)

# 결과를 새로운 엑셀 파일로 저장 (옵션)
data.to_excel('한국전기안전공단_리뷰.xlsx', index=False)

# 변경된 데이터 확인

