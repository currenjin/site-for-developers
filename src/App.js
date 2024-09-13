import "./components/css/App.css";
import { FaDiscord, FaBars } from "react-icons/fa6";
import { FaCheckCircle } from "react-icons/fa";
import { React } from "react";
import { Link, Route, Routes } from "react-router-dom";
import Home from "./pages/Home";
import About from "./pages/About";
import Contribute from "./pages/Contribute";

const App = () => {
  return (
    <div>
      <div className="navbar bg-base-100">
        <div className="navbar-start">
          <div className="dropdown">
            <div tabIndex={0} role="button" className="btn btn-ghost btn-circle">
              <FaBars size={30} />
            </div>
            <ul tabIndex={0}
              className="menu menu-sm dropdown-content mt-2 z-[1] border-2 bg-base-100 rounded-box w-[4.4rem]">
              <li><Link to="/">메인</Link></li>
              <li><Link to="/about">소개</Link></li>
              <li><Link to="/contribute">기여</Link></li>
            </ul>
          </div>
          <a className="btn btn-ghost text-xl font-bold" href="/">
            <img src="https://cdn.jsdelivr.net/gh/currenjin/site-for-developers/resources/icon_transparent/128x128/icon_transparent.svg" width="32" alt="Site For Developers logo" />
            Site for developers
          </a>
        </div>
        <div className="navbar-end">
          <button className="btn btn-ghost btn-circle">
            <a href="https://discord.gg/kdVAeDGx" rel="noreferrer" target="_blank">
              <FaDiscord size={30} />
            </a>
          </button>
          <button className="btn btn-ghost btn-circle">
            <a href="https://stats.uptimerobot.com/Klr3b7eDKs" rel="noreferrer" target="_blank">
              <FaCheckCircle size={30} />
            </a>
          </button>
        </div>
      </div>
      <div className="ml-2 mr-2">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/about" element={<About />} />
          <Route path="/contribute" element={<Contribute />} />
        </Routes>
      </div>
    </div>
  );
};

export default App;
