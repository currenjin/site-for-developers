import "./components/css/App.css";
import { React, useEffect } from "react";
import { IoMenu, IoSunny } from "react-icons/io5";
import { Route, Routes, Link } from "react-router-dom";
import Home from "./pages/Home";
import About from "./pages/About";
import Contribute from "./pages/Contribute";
import { themeChange } from "theme-change";

const App = () => {
  useEffect(() => {
    themeChange(false)
  }, [])
  return (
    <>
      <div className="navbar sticky top-0 z-50 bg-base-100">
        <div className="flex-none"></div>
        <div className="flex-1">
          <Link to="/">
            <div className="btn btn-ghost text-xl pretendard">
              💎 Site for developers
            </div>
          </Link>
        </div>
        <div className="flex-none">
          <label className="cursor-pointer grid place-items-center tooltip tooltip-bottom" data-tip="테마">
            <input type="checkbox" value="dark"
                   className="toggle theme-controller bg-base-content row-start-1 col-start-1 col-span-2"/>
            <svg className="col-start-1 row-start-1 stroke-base-100 fill-base-100" xmlns="http://www.w3.org/2000/svg"
                 width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"
                 strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="12" r="5"/>
              <path
                  d="M12 1v2M12 21v2M4.2 4.2l1.4 1.4M18.4 18.4l1.4 1.4M1 12h2M21 12h2M4.2 19.8l1.4-1.4M18.4 5.6l1.4-1.4"/>
            </svg>
            <svg className="col-start-2 row-start-1 stroke-base-100 fill-base-100" xmlns="http://www.w3.org/2000/svg"
                 width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"
                 strokeLinecap="round" strokeLinejoin="round">
              <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>
            </svg>
          </label>
          <div className="dropdown dropdown-hover dropdown-bottom dropdown-end">
            <div tabIndex={0} role="button" className="p-2">
              <IoMenu size={40}/>
            </div>
            <ul
                tabIndex={0}
                className="dropdown-content border-2 border-base-200 z-[1] menu p-1 bg-base-100 rounded-box w-52 suit text-base"
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
        <Route path="/" element={<Home/>}/>
        <Route path="/about" element={<About/>}/>
        <Route path="/contribute" element={<Contribute/>}/>
      </Routes>
    </>
  );
};

export default App;
