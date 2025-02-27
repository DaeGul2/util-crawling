import React, { useState } from "react";
import axios from "axios";

const NaverShoppingCrawling = () => {
    const [maxPages, setMaxPages] = useState(10); // 기본값 10페이지
    const [message, setMessage] = useState("");
    const [loading, setLoading] = useState(false);
    const [downloadUrl, setDownloadUrl] = useState(null);

    // 1️⃣ 브라우저 실행 (사용자가 직접 이동)
    const openBrowser = async () => {
        try {
            const response = await axios.get("http://localhost:5000/start-naver");
            setMessage(response.data.message);
        } catch (error) {
            console.error("브라우저 실행 오류", error);
            setMessage("브라우저 실행 중 오류 발생");
        }
    };

    // 2️⃣ 크롤링 시작
    const startCrawling = async () => {
        if (maxPages < 1) {
            setMessage("최대 페이지 수를 올바르게 입력하세요.");
            return;
        }

        setLoading(true);
        setMessage("");
        setDownloadUrl(null);

        try {
            const response = await axios.post("http://localhost:5000/naver-crawl", {
                max_pages: maxPages
            });
            setMessage(response.data.message);
            setDownloadUrl(response.data.download_url);
        } catch (error) {
            console.error("크롤링 실패", error);
            setMessage("크롤링 중 오류 발생");
        }

        setLoading(false);
    };

    return (
        <div>
            <h2>🛒 네이버 쇼핑 크롤링</h2>
            <button onClick={openBrowser} disabled={loading}>
                브라우저 실행 (상품 페이지 이동)
            </button>
            <input
                type="number"
                placeholder="최대 페이지 수"
                value={maxPages}
                onChange={(e) => setMaxPages(Number(e.target.value))}
                min="1"
            />
            <button onClick={startCrawling} disabled={loading}>
                {loading ? "크롤링 중..." : "크롤링 시작"}
            </button>
            {downloadUrl && (
                <div>
                    <p>✅ 크롤링 완료!</p>
                    <a href={downloadUrl} download>
                        <button>📥 결과 다운로드</button>
                    </a>
                </div>
            )}
            <p>{message}</p>
        </div>
    );
};

export default NaverShoppingCrawling;
