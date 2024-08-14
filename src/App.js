import "./components/css/App.css";
import { FaDiscord } from "react-icons/fa6";
import { FaCheckCircle } from "react-icons/fa";
import { React } from "react";
import { Link, Route, Routes } from "react-router-dom";
import Home from "./pages/Home";
import About from "./pages/About";
import Contribute from "./pages/Contribute";

const App = () => {
  return (
    <div>
      <div className="suit navbar bg-base-100">
        <div className="navbar-start">
          <div className="dropdown">
            <div tabIndex={0} role="button" className="btn btn-ghost btn-circle">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24"
                stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2"
                  d="M4 6h16M4 12h16M4 18h7" />
              </svg>
            </div>
            <ul tabIndex={0}
              className="menu menu-sm dropdown-content mt-3 z-[1] p-2 shadow bg-base-100 rounded-box w-52">
              <li><Link to="/">메인</Link></li>
              <li><Link to="/about">소개</Link></li>
              <li><Link to="/contribute">기여</Link></li>
            </ul>
          </div>
          <a className="btn btn-ghost text-xl">Site for developers</a>
        </div>
        <div className="navbar-end">
          <button className="btn btn-ghost btn-circle">
            <a href="https://discord.gg/kdVAeDGx" target="_blank">
              <FaDiscord size={30} />
            </a>
          </button>
          <button className="btn btn-ghost btn-circle">
            <a href="https://stats.uptimerobot.com/Klr3b7eDKs" target="_blank">
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
