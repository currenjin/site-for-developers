import "./components/css/App.css";
import { FaDiscord, FaBars } from "react-icons/fa6";
import { FaCheckCircle } from "react-icons/fa";
import { Link, Route, Routes } from "react-router-dom";
import Home from "./pages/Home";
import About from "./pages/About";
import Contribute from "./pages/Contribute";
import NotFound from "./pages/NotFound";

const App = () => {
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
              className="menu dropdown-content mt-2 z-[1] border-2 border-indigo-600 bg-base-100 rounded-lg w-42">
              <li><Link to="/">메인</Link></li>
              <li><Link to="/about">소개</Link></li>
              <li><Link to="/contribute">기여</Link></li>
              {/* Social (Mobile) */}
              <div className="block md:hidden">
                <li><a href="https://discord.gg/dRUBrU2t4J" rel="noreferrer" target="_blank">Discord</a></li>
                <li><a href="https://stats.uptimerobot.com/Klr3b7eDKs" rel="noreferrer" target="_blank">웹사이트 상태</a></li>
              </div>
            </ul>
          </div>
          <a className="btn btn-ghost text-xl" href="/">
            <img src="https://cdn.jsdelivr.net/gh/currenjin/site-for-developers/resources/icons/icon_transparent/128x128/icon_transparent.svg" width="36" alt="Site For Developers logo" />
            <p className="navbar_title text-indigo-600">Site For Developers</p>
          </a>
        </div>
        {/* Social (Desktop) */}
        <div className="navbar-end hidden md:flex">
          <button className="btn btn-ghost btn-circle">
            <a href="https://discord.gg/dRUBrU2t4J" rel="noreferrer" target="_blank">
              <FaDiscord size={26} />
            </a>
          </button>
          <button className="btn btn-ghost btn-circle">
            <a href="https://stats.uptimerobot.com/Klr3b7eDKs" rel="noreferrer" target="_blank">
              <FaCheckCircle size={26} />
            </a>
          </button>
        </div>
      </div>
      <div className="mx-2 mb-2">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/about" element={<About />} />
          <Route path="/contribute" element={<Contribute />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </div>
    </div>
  );
};

export default App;
