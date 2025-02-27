import "../components/css/pages.about.css";
import axios from "axios";
import { useState } from "react";

const About = () => {
  const [repositoryData, setrepositoryData] = useState([]);

  axios
    .get("https://api.github.com/repos/currenjin/site-for-developers")
    .then((response) => {
      console.log(response.data);
      setrepositoryData(response.data);
    });

    return (
        <div className="about">
            <div>명칭: Site For Developers</div>
            <div>소개: {repositoryData.description}</div>
            <div>주제: {repositoryData.topics + ""}</div>
            <div>개설일: {repositoryData.created_at}</div>
            <div>최근 업데이트: {repositoryData.updated_at}</div>
            <div>레포지토리 상태: {repositoryData.visibility}</div>
            <div>깃허브 주소: {repositoryData.html_url}</div>
            <div>웹사이트 주소: {repositoryData.homepage}</div>
            <div>스타 수: {repositoryData.stargazers_count}개</div>
            <div>구독자 수: {repositoryData.subscribers_count}명</div>
            <div>포크 횟수: {repositoryData.forks}회</div>
        </div>
    );
};

export default About;
