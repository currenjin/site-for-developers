import JSONContainer from "../components/js/JSONContainer";
import Index from "../components/js/Index";

const Home = () => {
  return (
    <div>
      {/* Index (Desktop) */}
      <aside className="md:block hidden fixed bottom-1 h-148 w-64 m-2 p-3 rounded-lg border-2 border-indigo-600 leading-7">
        <span className="m-2 text-2xl text-indigo-600 font-bold">목차</span><br />
        <Index />
      </aside>
      <main className="md:ml-68 w-auto">
        {/* Index (Mobile) */}
        <div tabIndex={0} className="md:hidden fixed bottom-2 right-2">
          <div className="dropdown dropdown-top dropdown-end">
            <div tabIndex={0} role="button" className="btn btn-ghost bg-indigo-600 text-xl text-white w-18 h-12 rounded-xl m-2 border-2">목차</div>
            <ul tabIndex={0} className="dropdown-content bg-base-100 rounded-box z-1 w-60 mr-2 p-2 border-indigo-600 border-2">
              <Index />
            </ul>
          </div>
        </div>
        <JSONContainer category="techcommunity" title="기술 커뮤니티" />
        <JSONContainer category="educationcommunity" title="교육 커뮤니티" paddingtop={true} />
        <JSONContainer category="news" title="뉴스" paddingtop={true} />
        <JSONContainer category="study" title="학습" paddingtop={true} />
        <JSONContainer category="codingtest" title="문제풀이" paddingtop={true} />
        <JSONContainer category="web" title="웹" paddingtop={true} />
        <JSONContainer category="design" title="디자인" paddingtop={true} />
        <JSONContainer category="programminglanguage" title="프로그래밍 언어" paddingtop={true} />
        <JSONContainer category="javascriptframework" title="자바스크립트 프레임워크" paddingtop={true} />
        <JSONContainer category="backendframework" title="백엔드 프레임워크" paddingtop={true} />
        <JSONContainer category="publiccloud" title="클라우드" paddingtop={true} />
        <JSONContainer category="mobile" title="모바일" paddingtop={true} />
        <JSONContainer category="database" title="데이터베이스" paddingtop={true} />
        <JSONContainer category="search" title="검색" paddingtop={true} />
        <JSONContainer category="linux" title="리눅스" paddingtop={true} />
        <JSONContainer category="infra" title="인프라" paddingtop={true} />
        <JSONContainer category="api" title="API" paddingtop={true} />
        <JSONContainer category="git" title="Git" paddingtop={true} />
        <JSONContainer category="other" title="기타" paddingtop={true} />
        <JSONContainer category="blog" title="블로그" paddingtop={true} />
        <JSONContainer category="video" title="동영상" paddingtop={true} />
        <JSONContainer category="collectionofdata" title="자료모음" paddingtop={true} />
        <JSONContainer category="tool" title="도구" paddingtop={true} />
        <JSONContainer category="nocode" title="노코드" paddingtop={true} />
        <JSONContainer category="json" title="JSON" paddingtop={true} />
        <JSONContainer category="regex" title="정규 표현식" paddingtop={true} />
        <JSONContainer category="codeformatter" title="코드 포매터" paddingtop={true} />
        <JSONContainer category="ide" title="IDE" paddingtop={true} />
        <JSONContainer category="ai" title="AI" paddingtop={true} />
      </main>
    </div>
  );
};

export default Home;
