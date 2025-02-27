import React, { useState } from "react";
import axios from "axios";

const CrawlButton = () => {
    const [url, setUrl] = useState("");
    const [message, setMessage] = useState("");
    const [loading, setLoading] = useState(false);

    // 1️⃣ 브라우저 실행 (로그인용)
    const openBrowser = async () => {
        try {
            const response = await axios.get("http://localhost:5000/start");
            setMessage(response.data.message);
        } catch (error) {
            console.error("브라우저 실행 오류", error);
            setMessage("브라우저 실행 중 오류 발생");
        }
    };

    // 2️⃣ 크롤링 시작
    const startCrawling = async () => {
        if (!url) {
            setMessage("URL을 입력하세요.");
            return;
        }

        setLoading(true);
        setMessage("");

        try {
            const response = await axios.post("http://localhost:5000/crawl", {
                target_url: url
            });
            setMessage(response.data.message);
        } catch (error) {
            console.error("크롤링 실패", error);
            setMessage("크롤링 중 오류 발생");
        }

        setLoading(false);
    };

    return (
        <div>
            <h2>크롤링 시스템</h2>
            <input
                type="text"
                placeholder="크롤링할 URL 입력"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
            />
            <button onClick={openBrowser} disabled={loading}>
                브라우저 실행 (로그인)
            </button>
            <button onClick={startCrawling} disabled={loading}>
                {loading ? "크롤링 중..." : "크롤링 시작"}
            </button>
            <p>{message}</p>
        </div>
    );
};

export default CrawlButton;
