const express = require("express");
const axios = require("axios");
const cors = require("cors");
const crypto = require("crypto"); // ✅ crypto 모듈 올바르게 가져오기
require("dotenv").config();

const app = express();
const PORT = 5000;

app.use(cors());
app.use(express.json());

const CLIENT_ID = "MnmJgZoru9FA6WicxRxO";
const CLIENT_SECRET = "KnCvscYqOd";

const NAVER_API_URL = "https://api.naver.com";
const ACCESS_LICENSE = process.env.NAVER_ACCESS_LICENSE;
const SECRET_KEY = process.env.NAVER_SECRET_KEY;
const CUSTOMER_ID = process.env.NAVER_CUSTOMER_ID;


function generateSignature(timestamp, method, uri, secretKey) {
    const message = `${timestamp}.${method}.${uri}`;
    const hmac = crypto.createHmac('sha256', secretKey);
    hmac.update(message);
    return hmac.digest('base64');
}



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
// ✅ 검색량 조회 API (POST 요청으로 변경)
app.post("/api/search-volume", async (req, res) => {
    try {
        console.log("📌 입력된 키워드:", req.body.keywords);

        const inputText = req.body.keywords;
        if (!inputText) {
            return res.status(400).json({ error: "keywords 값을 보내야 합니다." });
        }

        const keywords = inputText.split(",").map(k => k.trim()).filter(k => k.length > 0);
        const uri = "/keywordstool";
        const method = "POST";  
        const timestamp = Date.now().toString();
        const signature = generateSignature(timestamp, method, uri, SECRET_KEY);

        const requestBody = {
            hintKeywords: keywords,  // ✅ 배열 형태로 전달
            showDetail: 1
        };

        console.log("📌 API 요청 데이터:", JSON.stringify(requestBody, null, 2));

        const response = await axios.post(`${NAVER_API_URL}${uri}`, requestBody, {
            headers: {
                "X-API-KEY": ACCESS_LICENSE,
                "X-Customer": CUSTOMER_ID,
                "X-Signature": signature,
                "X-Timestamp": timestamp,
                "Content-Type": "application/json",
                "X-Api-Format": "json",
            }
        });

        console.log("📌 API 응답 데이터:", response.data);

        if (!response.data.keywordList || response.data.keywordList.length === 0) {
            console.warn("⚠️ 검색량 데이터 없음 (네이버 API에서 반환된 데이터가 없음)");
            return res.status(404).json({ error: "검색량 데이터를 찾을 수 없습니다." });
        }

        const result = response.data.keywordList.map(item => ({
            keyword: item.relKeyword,
            pc_search: item.monthlyPcQcCnt || 0,
            mobile_search: item.monthlyMobileQcCnt || 0
        }));

        res.json(result);
    } catch (error) {
        console.error("🔴 네이버 검색량 API 요청 실패:", error);
        res.status(500).json({ error: "네이버 검색량 API 호출 중 오류 발생" });
    }
});

// ✅ 서버 실행
app.listen(PORT, () => {
    console.log(`🚀 서버 실행 중: http://localhost:${PORT}`);
});
