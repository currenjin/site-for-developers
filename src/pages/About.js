import "../components/css/pages.about.css";
import axios from "axios";
import {useState, React} from "react";

const About = () => {
    const [repositoryData, setrepositoryData] = useState([]);

    axios
        .get("https://api.github.com/repos/currenjin/site-for-developers")
        .then((response) => {
            console.log(response.data);
            setrepositoryData(response.data);
        });

    return (
        <div className="suit repositorydata">
            <div className="p-2 mb-2 rounded-lg border-2">명칭: Site For Developers</div>
            <div className="p-2 mb-2 rounded-lg border-2">소개: {repositoryData.description}</div>
            <div className="p-2 mb-2 rounded-lg border-2">주제: {repositoryData.topics + " "}</div>
            <div className="p-2 mb-2 rounded-lg border-2">개설일: {repositoryData.created_at}</div>
            <div className="p-2 mb-2 rounded-lg border-2">최근 업데이트: {repositoryData.updated_at}</div>
            <div className="p-2 mb-2 rounded-lg border-2">레포지토리 상태: {repositoryData.visibility}</div>
            <div className="p-2 mb-2 rounded-lg border-2">깃허브 주소: {repositoryData.html_url}</div>
            <div className="p-2 mb-2 rounded-lg border-2">웹사이트 주소: {repositoryData.homepage}</div>
            <div className="p-2 mb-2 rounded-lg border-2">스타 수: {repositoryData.stargazers_count}개</div>
            <div className="p-2 mb-2 rounded-lg border-2">구독자 수: {repositoryData.subscribers_count}명</div>
            <div className="p-2 mb-2 rounded-lg border-2">포크 횟수: {repositoryData.forks}번</div>
        </div>
    );
};

export default About;
