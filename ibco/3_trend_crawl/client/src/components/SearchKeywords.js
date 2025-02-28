import React, { useState } from "react";
import { fetchRelatedKeywords } from "../services/naverApi";
import KeywordResults from "./KeywordResults";

const SearchKeywords = () => {
    const [input, setInput] = useState("");
    const [keywords, setKeywords] = useState([]);
    const [relatedKeywords, setRelatedKeywords] = useState({});
    const [loading, setLoading] = useState(false);

    const handleSearch = async () => {
        const keywordList = input.split(",").map(k => k.trim()).filter(k => k);
        if (keywordList.length === 0) return;

        setLoading(true);
        const results = await fetchRelatedKeywords(keywordList);
        setRelatedKeywords(results);
        setKeywords(keywordList);
        setLoading(false);
    };

    return (
        <div style={{ textAlign: "center", maxWidth: "600px", margin: "auto" }}>
            <h2>🔍 키워드 검색</h2>
            <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="키워드를 쉼표(,)로 구분하여 입력"
                style={{ width: "80%", padding: "8px" }}
            />
            <button onClick={handleSearch} style={{ marginLeft: "10px", padding: "8px" }}>
                검색
            </button>

            {loading && <p>검색 중...</p>}

            {Object.keys(relatedKeywords).length > 0 && (
                <KeywordResults relatedKeywords={relatedKeywords} />
            )}
        </div>
    );
};

export default SearchKeywords;
