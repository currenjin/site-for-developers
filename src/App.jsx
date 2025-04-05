import "./components/css/App.css";
import { useState } from "react";
import { FaCheckCircle, FaBars, FaGithub } from "react-icons/fa";
import { Link, Route, Routes } from "react-router-dom";
import Home from "./pages/Home";
import About from "./pages/About";
import Contribute from "./pages/Contribute";
import NotFound from "./pages/NotFound";

const App = () => {
  const [searchInput, setSearchInput] = useState("");

  return (
    <div>
      {/* Navbar */}
      <div className="navbar bg-base-100">
        <div className="navbar-start">
          <div className="dropdown">
            <div tabIndex={0} role="button" className="btn btn-ghost btn-circle ml-1">
              <FaBars size={26} />
            </div>
            <ul tabIndex={0}
              className="menu dropdown-content mt-2 z-[1] border border-indigo-600 bg-base-100 rounded-2xl w-42">
              <li><Link to="/">메인</Link></li>
              <li><Link to="/about">소개</Link></li>
              <li><Link to="/contribute">기여</Link></li>
              {/* Social (Mobile) */}
              <div className="block md:hidden">
                <li><a href="https://github.com/currenjin/site-for-developers" rel="noreferrer" target="_blank">GitHub</a></li>
                <li><a href="https://stats.uptimerobot.com/Klr3b7eDKs" rel="noreferrer" target="_blank">웹사이트 상태</a></li>
              </div>
            </ul>
          </div>
          <a className="btn btn-ghost text-xl" href="/">
            <img src="https://cdn.jsdelivr.net/gh/currenjin/site-for-developers/resources/icons/icon_transparent/64x64/icon_transparent.svg" width="36" alt="Site For Developers logo" />
            <p className="navbar_title text-indigo-600 md:block hidden">Site For Developers</p>
          </a>
        </div>
        {/* Social (Desktop) */}
        <div className="navbar-end">
          <label className="input mr-2">
            <svg className="h-[1em] opacity-50" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><g strokeLinejoin="round" strokeLinecap="round" strokeWidth="2.5" fill="none" stroke="currentColor"><circle cx="11" cy="11" r="8"></circle><path d="m21 21-4.3-4.3"></path></g></svg>
            <input type="search" className="grow" placeholder="검색어를 입력하세요" onChange={(e) => setSearchInput(e.target.value)} />
          </label>
          <div className="hidden md:flex">
          <button className="btn btn-ghost btn-circle">
            <a href="https://github.com/currenjin/site-for-developers" rel="noreferrer" target="_blank">
              <FaGithub size={26} />
            </a>
          </button>
          <button className="btn btn-ghost btn-circle">
            <a href="https://stats.uptimerobot.com/Klr3b7eDKs" rel="noreferrer" target="_blank">
              <FaCheckCircle size={26} />
            </a>
          </button>
          </div>
        </div>
      </div>
      <div className="mx-2 mb-2">
        <Routes>
          <Route path="/" element={<Home searchInput={searchInput} />} />
          <Route path="/about" element={<About />} />
          <Route path="/contribute" element={<Contribute />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </div>
    </div>
  );
};

export default App;
