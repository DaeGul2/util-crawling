import React from "react";
import { Link } from "react-router-dom";

const Navbar = () => {
    return (
        <nav>
            <ul>
                <li><Link to="/">🏠 홈</Link></li>
                <li><Link to="/jobplanet">💼 잡플래닛 크롤링</Link></li>
                <li><Link to="/naver-shopping">🛒 네이버 쇼핑 리뷰 크롤링</Link></li>
                <li><Link to="/naver-price-review">💰 네이버 가격 리뷰 크롤링</Link></li>
            </ul>
        </nav>
    );
};

export default Navbar;
