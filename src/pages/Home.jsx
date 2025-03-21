import axios from "axios";
import { useEffect, useState } from "react";
import JSONContainer from "../components/js/JSONContainer";
import Index from "../components/js/Index";

const Home = () => {

  const [data, setData] = useState([]);

  useEffect(() => {
    axios
      .get(
        "https://cdn.jsdelivr.net/gh/currenjin/site-for-developers/data.json"
      )
      .then((response) => {
        setData(response.data);
        console.log(response.data);
      });
  }, []);

  return (
    <div>
      {/* Index (Desktop) */}
      <aside className="md:block hidden fixed h-fit w-68 mx-2 p-3 rounded-2xl border-2 border-indigo-600 leading-7.5">
        <span className="m-2 text-3xl text-indigo-600 font-bold">목차</span><br />
        <Index />
      </aside>
      <main className="md:ml-73 w-auto my-4">
        {/* Index (Mobile) */}
        <div className="md:hidden dropdown dropdown-top dropdown-end fixed bottom-2 right-2">
          <button tabIndex={0} className="btn btn-ghost bg-indigo-600 text-xl text-white w-18 h-12 rounded-2xl m-2 border-2">목차</button>
          <ul tabIndex={0} className="dropdown-content bg-base-100 rounded-2xl z-1 w-60 mr-2 p-2 border-indigo-600 border-2">
            <Index />
          </ul>
        </div>
        <JSONContainer category="techcommunity" title="기술 커뮤니티" data={data} paddingtop={false} />
        <JSONContainer category="educationcommunity" title="교육 커뮤니티" data={data} />
        <JSONContainer category="news" title="뉴스" data={data} />
        <JSONContainer category="study" title="학습" data={data} />
        <JSONContainer category="codingtest" title="문제풀이" data={data} />
        <JSONContainer category="web" title="웹" data={data} />
        <JSONContainer category="design" title="디자인" data={data} />
        <JSONContainer category="programminglanguage" title="프로그래밍 언어" data={data} />
        <JSONContainer category="javascriptframework" title="자바스크립트 프레임워크" data={data} />
        <JSONContainer category="backendframework" title="백엔드 프레임워크" data={data} />
        <JSONContainer category="publiccloud" title="클라우드" data={data} />
        <JSONContainer category="mobile" title="모바일" data={data} />
        <JSONContainer category="database" title="데이터베이스" data={data} />
        <JSONContainer category="search" title="검색" data={data} />
        <JSONContainer category="linux" title="리눅스" data={data} />
        <JSONContainer category="infra" title="인프라" data={data} />
        <JSONContainer category="api" title="API" data={data} />
        <JSONContainer category="git" title="Git" data={data} />
        <JSONContainer category="other" title="기타" data={data} />
        <JSONContainer category="blog" title="블로그" data={data} />
        <JSONContainer category="video" title="동영상" data={data} />
        <JSONContainer category="collectionofdata" title="자료모음" data={data} />
        <JSONContainer category="tool" title="도구" data={data} />
        <JSONContainer category="nocode" title="노코드" data={data} />
        <JSONContainer category="json" title="JSON" data={data} />
        <JSONContainer category="regex" title="정규 표현식" data={data} />
        <JSONContainer category="codeformatter" title="코드 포매터" data={data} />
        <JSONContainer category="ide" title="IDE" data={data} />
        <JSONContainer category="ai" title="AI" data={data} />
      </main>
    </div>
  );
};

export default Home;
