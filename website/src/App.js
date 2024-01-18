import "./css/App.css";
import { React } from "react";
import { IoClose, IoMenu } from "react-icons/io5";
import { Route, Routes, Link } from "react-router-dom";
import Home from "./pages/Home";
import About from "./pages/About";
import Contribute from "./pages/Contribute";

const App = () => {
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
          현재 목차를 클릭하였을 때 정상적으로 작동하지 않는 오류가 있어요.
          자세한 내용을 보려면{" "}
          <a href="https://github.com/currenjin/site-for-developers/issues/9">
            여기
          </a>
          를 클릭하세요.
        </div>
        <div className="justify-end">
          <button className="bg-gray-300 p-2 rounded-lg" onClick={closeBanner}>
            <IoClose size={22} />
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
        <div className="flex-none">
          <div className="dropdown dropdown-hover dropdown-bottom dropdown-end">
            <div tabIndex={0} role="button" className="p-2">
              <IoMenu size={40} />
            </div>
            <ul
              tabIndex={0}
              className="dropdown-content z-[1] menu p-1 shadow bg-base-100 rounded-box w-52 suit text-base"
            >
              <li>
                <Link to="/">홈</Link>
              </li>
              <li>
                <Link to="/about">소개</Link>
              </li>
              <li>
                <Link to="/contribute">기여</Link>
              </li>
            </ul>
          </div>
        </div>
      </div>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/about" element={<About />} />
        <Route path="/contribute" element={<Contribute />} />
      </Routes>
    </>
  );
};

export default App;
