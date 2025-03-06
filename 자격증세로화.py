import pandas as pd

# 엑셀 파일 읽기
input_file = "input.xlsx"
output_file = "자격증세로화된거.xlsx"
sheet_name = "자격증"

# '경력사항' 시트 읽기
df = pd.read_excel(input_file, sheet_name=sheet_name)

# 컬럼명 리스트
columns = df.columns.tolist()

# '회원번호' 컬럼을 고정값으로 설정
fixed_columns = ["회원번호"]

# '회사명' 포함된 컬럼 찾기 (세트 구분용)
company_columns = [col for col in columns if "자격증명" in col]
set_indices = [columns.index(col) for col in company_columns]

# ✅ 세트 내 컬럼 순서를 input에서 등장한 순서대로 유지
set_columns_order = []
for col in columns:
    base_col_name = col.rstrip('0123456789')  # 숫자 제거
    if base_col_name not in fixed_columns and base_col_name not in set_columns_order:
        set_columns_order.append(base_col_name)

# 변환된 데이터 저장 리스트
output_data = []

for _, row in df.iterrows():
    # 공통 정보 (회원번호만 유지)
    common_data = {col: row[col] for col in fixed_columns if col in row}

    temp_data = []  # 정렬 전 데이터를 임시 저장

    # 경력이 없는 경우 체크
    is_empty = all(pd.isna(row[col]) or row[col] == "" for col in company_columns)

    if is_empty:
        # 경력이 없는 경우 한 줄만 출력
        empty_record = common_data.copy()
        empty_record["자격증연번"] = 1
        empty_record["자격증명"] = "기재 자격증 없음"
        output_data.append(empty_record)
    else:
        # 경력이 있는 경우, 세트별 데이터 저장
        for i in range(len(set_indices)):
            start_idx = set_indices[i]
            end_idx = set_indices[i + 1] if i + 1 < len(set_indices) else len(columns)

            # 현재 세트의 컬럼명 리스트
            set_columns = columns[start_idx:end_idx]

            # 해당 세트의 '회사명'이 비어있으면 스킵
            if pd.isna(row[set_columns[0]]) or row[set_columns[0]] == "":
                continue

            # ✅ 세트별 데이터 저장 (숫자 제거한 컬럼명만 유지)
            set_data = {col.rstrip('0123456789'): row[col] for col in set_columns}

            # ✅ 한 줄의 데이터로 저장 (회원번호 + 한 세트의 데이터만 포함)
            record = {**common_data, **set_data}
            temp_data.append(record)

        # ✅ '근무기간(시작)'을 기준으로 과거 순 정렬
        temp_data.sort(key=lambda x: x.get("취득시기", pd.NaT) or pd.Timestamp.max)

        # ✅ 정렬된 후에 '경력연번'을 부여
        for idx, record in enumerate(temp_data, start=1):
            record["자격증연번"] = idx
            output_data.append(record)

# DataFrame 변환
output_df = pd.DataFrame(output_data)

# ✅ 최종 컬럼 구성 (회원번호 + 경력연번 + 세트 컬럼을 input 등장 순서대로 정렬)
final_columns = ["회원번호", "자격증연번"] + set_columns_order

# ✅ 존재하는 컬럼만 필터링
output_df = output_df[[col for col in final_columns if col in output_df.columns]]

# 엑셀 저장
output_df.to_excel(output_file, index=False)

print(f"파일이 {output_file}로 저장되었습니다.")
