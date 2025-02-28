import axios from "axios";

const API_BASE_URL = "http://localhost:5000/api";

// 🔹 연관 키워드 가져오기
export const fetchRelatedKeywords = async (keywords) => {
    try {
        const response = await axios.post(`${API_BASE_URL}/related-keywords`, { keywords });
        return response.data;
    } catch (error) {
        console.error("🔴 연관 키워드 가져오기 실패:", error);
        return {};
    }
};

// 🔹 특정 키워드의 상품 개수 가져오기
export const fetchProductCount = async (keyword) => {
    try {
        const response = await axios.get(`${API_BASE_URL}/product-count`, {
            params: { keyword }
        });
        return response.data.totalResults;
    } catch (error) {
        console.error("🔴 상품 개수 가져오기 실패:", error);
        return "N/A"; // ✅ 오류 발생 시 "N/A" 반환
    }
};
