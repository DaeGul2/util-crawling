const express = require("express");
const axios = require("axios");
const cors = require("cors");

const app = express();
const PORT = 5000;

app.use(cors());
app.use(express.json());

const CLIENT_ID = "MnmJgZoru9FA6WicxRxO";
const CLIENT_SECRET = "KnCvscYqOd";

// ✅ 연관 키워드 가져오기
app.post("/api/related-keywords", async (req, res) => {
    const { keywords } = req.body;  // 키워드 리스트 받음

    if (!keywords || !Array.isArray(keywords)) {
        return res.status(400).json({ error: "키워드 리스트가 필요합니다." });
    }

    try {
        let results = {};
        for (let keyword of keywords) {
            const response = await axios.get("https://openapi.naver.com/v1/search/shop.json", {
                headers: {
                    "X-Naver-Client-Id": CLIENT_ID,
                    "X-Naver-Client-Secret": CLIENT_SECRET
                },
                params: { query: keyword, display: 50 } // ✅ 연관 키워드 최대 5개 가져오기
            });

            // 🔹 <b> 태그 제거
            results[keyword] = response.data.items.map(item => item.title.replace(/<\/?b>/g, ""));
        }

        res.json(results);
    } catch (error) {
        console.error("🔴 연관 키워드 요청 실패:", error);
        res.status(500).json({ error: "네이버 API 요청 실패" });
    }
});

// ✅ 특정 키워드의 등록된 상품 개수 가져오기
app.get("/api/product-count", async (req, res) => {
    const { keyword } = req.query;

    if (!keyword) {
        return res.status(400).json({ error: "키워드가 필요합니다." });
    }

    try {
        const response = await axios.get("https://openapi.naver.com/v1/search/shop.json", {
            headers: {
                "X-Naver-Client-Id": CLIENT_ID,
                "X-Naver-Client-Secret": CLIENT_SECRET
            },
            params: { query: keyword, display: 100 } // ✅ 상품 개수 정확히 가져오기 위해 100개로 설정
        });

        const totalResults = response.data.total;

        // 🔹 상품 개수가 0이면 클라이언트에서 리스트에서 제외하도록 설정
        res.json({ keyword, totalResults: totalResults > 0 ? totalResults : "N/A" });
    } catch (error) {
        console.error("🔴 상품 개수 요청 실패:", error);
        res.status(500).json({ error: "네이버 API 요청 실패" });
    }
});

// ✅ 서버 실행
app.listen(PORT, () => {
    console.log(`🚀 서버 실행 중: http://localhost:${PORT}`);
});
