import "./css/App.css";
import { React } from "react";
import { IoMenu } from "react-icons/io5";
import { Route, Routes, Link } from "react-router-dom";
import Home from "./pages/Home";
import About from "./pages/About";
import Contribute from "./pages/Contribute";

const App = () => {
  return (
    <>
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
