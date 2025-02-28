import React, { useState } from "react";
import { fetchProductCount } from "../services/naverApi";
import "bootstrap/dist/css/bootstrap.min.css"; // Bootstrap 스타일 적용

// HTML 태그 제거 함수
const removeHtmlTags = (text) => text.replace(/<[^>]*>/g, "");

const KeywordResults = ({ relatedKeywords }) => {
    const [productCounts, setProductCounts] = useState({});

    const handleClick = async (keyword) => {
        if (productCounts[keyword] !== undefined) return; // 이미 조회된 경우 중복 조회 방지

        const count = await fetchProductCount(keyword);
        setProductCounts(prev => ({ ...prev, [keyword]: count }));
    };

    return (
        <div className="container mt-4">
            <h3 className="mb-3">📌 연관 키워드</h3>
            <div className="row">
                {Object.entries(relatedKeywords).map(([keyword, words]) => (
                    <div key={keyword} className="col-md-6">
                        <div className="card mb-3">
                            <div className="card-header">
                                <h5 className="mb-0">🔹 {removeHtmlTags(keyword)}</h5>
                            </div>
                            <ul className="list-group list-group-flush">
                                {words.map((word, index) => (
                                    <li
                                        key={index}
                                        className="list-group-item d-flex justify-content-between align-items-center"
                                        style={{ cursor: "pointer" }}
                                        onClick={() => handleClick(word)}
                                    >
                                        <span>{removeHtmlTags(word)}</span>
                                        {productCounts[word] !== undefined && (
                                            <span className="badge bg-primary rounded-pill">
                                                {productCounts[word]}개
                                            </span>
                                        )}
                                    </li>
                                ))}
                            </ul>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default KeywordResults;
