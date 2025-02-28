import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";
import JobPlanetCrawling from "./components/JobPlanetCrawling";
import NaverShoppingCrawling from "./components/NaverShoppingCrawling";
import NaverPriceReviewCrawling from "./components/NaverPriceReviewCrawling";

function App() {
    return (
        <Router>
            <Navbar />
            <Routes>
                <Route path="/" element={<h1>🏠 홈페이지</h1>} />
                <Route path="/jobplanet" element={<JobPlanetCrawling />} />
                <Route path="/naver-shopping" element={<NaverShoppingCrawling />} />
                <Route path="/naver-price-review" element={<NaverPriceReviewCrawling />} />
            </Routes>
        </Router>
    );
}

export default App;
