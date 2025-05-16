import "./components/css/App.css";
import { useState } from "react";
import { BsList, BsGithub, BsCheckCircleFill, BsQuestionCircle, BsBook, BsHouse, BsCollection } from "react-icons/bs";
import { Link, Route, Switch } from "wouter";
import Home from "./pages/Home";
import About from "./pages/About";
import Contribute from "./pages/Contribute";
import Index from "./components/js/Index";

const App = () => {
  const [searchInput, setSearchInput] = useState("");

  return (
    <div>
      {/* Navbar */}
      <div className="navbar bg-base-100 border-b-2 border-gray-300 dark:border-gray-600">
        <div className="navbar-start">
          <div className="dropdown md:block hidden">
            <div tabIndex={0} role="button" className="btn btn-ghost btn-circle">
              <BsList size={32} />
            </div>
            <ul tabIndex={0}
              className="menu dropdown-content mt-2 z-[1] border-2 border-gray-300 dark:border-gray-600 dark:border-gray-600 dark:border-gray-600 dark:border-gray-600 dark:border-gray-600 dark:border-gray-600 bg-base-100 rounded-2xl w-42">
              <li><Link to="/"><span className="dark:text-neutral-content">메인</span></Link></li>
              <li><Link to="/about"><span className="dark:text-neutral-content">소개</span></Link></li>
              <li><Link to="/contribute"><span className="dark:text-neutral-content">기여</span></Link></li>
            </ul>
          </div>
          <a className="btn btn-ghost text-xl" href="/">
            <img src="https://cdn.jsdelivr.net/gh/currenjin/site-for-developers/resources/icons/icon_transparent/64x64/icon_transparent.svg" width="36" alt="Site For Developers logo" />
            <p className="navbar_title text-indigo-600 md:block hidden">Site For Developers</p>
          </a>
        </div>
        <div className="navbar-end">
          <label className="input mr-2">
            <svg className="h-[1em] opacity-50" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><g strokeLinejoin="round" strokeLinecap="round" strokeWidth="2.5" fill="none" stroke="currentColor"><circle cx="11" cy="11" r="8"></circle><path d="m21 21-4.3-4.3"></path></g></svg>
            <input type="search" className="grow" placeholder="검색어를 입력하세요" onChange={(e) => setSearchInput(e.target.value)} />
          </label>
          <div className="hidden md:flex">
            <button className="btn btn-ghost btn-circle">
              <a href="https://github.com/currenjin/site-for-developers" rel="noreferrer" target="_blank">
                <BsGithub size={25} className="dark:text-neutral-content" />
              </a>
            </button>
            <button className="btn btn-ghost btn-circle">
              <a href="https://stats.uptimerobot.com/Klr3b7eDKs" rel="noreferrer" target="_blank">
                <BsCheckCircleFill size={25} className="dark:text-neutral-content" />
              </a>
            </button>
          </div>
        </div>
      </div>
      <div className="m-2">
        <Switch>
          <Route path="/"><Home searchInput={searchInput} /></Route>
          <Route path="/about" component={About} />
          <Route path="/contribute" component={Contribute} />
          <Route>404 페이지를 찾을 수 없습니다 <br /> <a href="/">홈으로 돌아가기</a></Route>
        </Switch>
      </div>
      {/* Navbar (Mobile) */}
      <div className="dock md:hidden flex">
        <Link to="/">
          <button>
            <BsHouse size={24} />
          </button>
        </Link>

        <Link to="/about">
          <button>
            <BsQuestionCircle size={24} />
          </button>
        </Link>

        <Link to="/contribute">
          <button>
            <BsBook size={24} />
          </button>
        </Link>

        <button>
          <button onClick={() => document.getElementById('my_modal_1').showModal()}><BsCollection size={24} /></button>
          <dialog id="my_modal_1" className="modal">
            <div className="modal-box">
              <h3 className="font-bold text-lg">목차</h3>
              <p className="py-4"><Index /></p>
              <div className="modal-action">
                <form method="dialog">
                  <button className="btn">닫기</button>
                </form>
              </div>
            </div>
          </dialog>
        </button>
      </div>
    </div>
  );
};

export default App;
