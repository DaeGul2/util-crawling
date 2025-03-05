import React from "react";
import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom";
import SearchKeywords from "./components/SearchKeywords";
import SearchVolumeTable from "./components/SearchVolumeTable";

function App() {
    return (
        <Router>
            <div style={{ padding: "20px", textAlign: "center" }}>
                <h1>🔍 네이버 키워드 검색 시스템</h1>
                <nav style={{ marginBottom: "20px" }}>
                    <Link to="/" style={{ marginRight: "15px" }}>연관 키워드 검색</Link>
                    <Link to="/search-volume">검색량 조회</Link>
                </nav>
                <Routes>
                    <Route path="/" element={<SearchKeywords />} />
                    <Route path="/search-volume" element={<SearchVolumeTable />} />
                </Routes>
            </div>
        </Router>
    );
}

export default App;
