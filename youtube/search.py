import requests
import pandas as pd
import re

# 🔑 API 키 설정
API_KEY = "AIzaSyASVNuhVLTae-KvbKckbyu7aatED82R11A"
BASE_URL = "https://www.googleapis.com/youtube/v3"

# 🎯 특정 키워드 검색 (조회수 기준 정렬)
def search_videos(keyword, max_results=50):
    url = f"{BASE_URL}/search"
    params = {
        "part": "snippet",
        "q": keyword,
        "type": "video",
        "order": "viewCount",  # 조회수 순 정렬
        "maxResults": max_results,
        "key": API_KEY
    }
    response = requests.get(url, params=params)
    return response.json()

# 🎬 영상 상세 정보 가져오기 (조회수, 좋아요 수, 댓글 수, 설명란 포함)
def get_video_details(video_ids):
    url = f"{BASE_URL}/videos"
    params = {
        "part": "snippet,statistics",
        "id": ",".join(video_ids),
        "key": API_KEY
    }
    response = requests.get(url, params=params)
    return response.json()

# 🎼 BGM 정보 파싱 (설명란에서 배경음악 관련 정보 추출)
def extract_bgm_info(description):
    if not description:
        return "No Music Info"
    
    # BGM 관련 키워드 리스트
    bgm_keywords = ["Music by", "Soundtrack", "BGM", "배경음악", "노래", "Song"]
    bgm_info = []

    # 한 줄씩 파싱하며 BGM 관련 키워드 포함된 줄 찾기
    for line in description.split("\n"):
        if any(keyword.lower() in line.lower() for keyword in bgm_keywords):
            bgm_info.append(line.strip())

    return " | ".join(bgm_info) if bgm_info else "No Music Info"

# 🚀 실행 함수
def fetch_youtube_video_data(keyword="고양이", max_results=50):
    print(f"🔎 '{keyword}' 유튜브 검색 중...")
    search_result = search_videos(keyword, max_results)
    video_ids = [item["id"]["videoId"] for item in search_result.get("items", [])]
    
    print(f"🎬 {len(video_ids)}개의 영상 발견!")
    video_details = get_video_details(video_ids)

    data = []
    
    for video in video_details.get("items", []):
        title = video["snippet"]["title"]
        channel = video["snippet"]["channelTitle"]
        video_url = f"https://www.youtube.com/watch?v={video['id']}"
        views = video["statistics"].get("viewCount", "N/A")
        likes = video["statistics"].get("likeCount", "N/A")
        comments = video["statistics"].get("commentCount", "N/A")
        description = video["snippet"].get("description", "No Description")

        # 🎼 BGM 정보 추출
        bgm_info = extract_bgm_info(description)

        data.append([title, channel, video_url, views, likes, comments, description, bgm_info])

    # 📁 엑셀 저장
    df = pd.DataFrame(data, columns=["영상 제목", "업로더", "링크", "조회수", "좋아요 수", "댓글 수", "설명란", "BGM 정보"])
    df.to_excel("youtube_video_data_임신_샴푸.xlsx", index=False)
    print("✅ youtube_video_data_임산부.xlsx 파일 저장 완료!")

# 🔥 실행
fetch_youtube_video_data("임신 샴푸", 100)
