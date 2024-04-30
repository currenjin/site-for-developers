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
            <span>이름: {repositoryData.full_name}</span>
            <br/>
            <span>소개: {repositoryData.description}</span>
            <br/>
            <span>개설일: {repositoryData.created_at}</span>
            <br/>
            <span>최근 업데이트: {repositoryData.updated_at}</span>
            <br/>
            <span>웹사이트 주소: {repositoryData.homepage}</span>
            <br/>
            <span>스타 수: {repositoryData.stargazers_count}개</span>
        </div>
    );
};

export default About;
