import "../components/css/pages.notfound.css";
import { React } from "react";
import { Link } from 'react-router-dom';

const NotFound = () => {
    return (
        <div className="p-2 rounded-lg border-2">
            <p align="middle">
                <span className="text-6xl">404 Not Found</span>
                <br/>
                <span className="text-2xl">페이지를 찾을 수 없습니다.</span>
                <br/>
                <Link to="/">홈으로 돌아가기</Link>
            </p>
        </div>
    );
};

export default NotFound;
