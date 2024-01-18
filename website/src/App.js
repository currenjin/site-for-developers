import "./App.css";
import { useState, React } from "react";
import { IoClose } from "react-icons/io5";
import { marked } from "marked";
import axios from "axios";

const App = () => {
  const [mdData, setmdData] = useState([]);

  axios
    .get("https://cdn.jsdelivr.net/gh/currenjin/site-for-developers/README.md")
    .then((response) => {
      console.log(marked.parse(response.data));
      setmdData(marked.parse(response.data));
    });

  function closeBanner() {
    var banner = document.getElementById("banner");
    banner.style.display = "none";
  }
  return (
    <>
      <div
        className="banner flex items-center justify-between w-full bg-gray-200 p-4 suit"
        id="banner"
      >
        <div className="justify-start">
          목차를 클릭하였을 때 정상적으로 작동하지 않는 오류가 있어요. 자세한
          내용을 보려면{" "}
          <a href="https://github.com/currenjin/site-for-developers/issues/9">
            여기
          </a>
          를 클릭하세요.
        </div>
        <div className="justify-end">
          <button className="bg-gray-400 p-2 rounded-lg" onClick={closeBanner}>
            <IoClose size={26} />
          </button>
        </div>
      </div>
      <div className="navbar bg-base-100">
        <div className="flex-none"></div>
        <div className="flex-1">
          <div className="btn btn-ghost text-xl suit">
            💎 Site for developers
          </div>
        </div>
        <div className="flex-none"></div>
      </div>
      <div
        className="ml-4 mr-4 mb-4 p-4 rounded-lg bg-gray-200 pretendard"
        dangerouslySetInnerHTML={{ __html: mdData }}
      ></div>
    </>
  );
};

export default App;
