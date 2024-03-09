import "./components/css/App.css";
import { React } from "react";
import { Navbar, Banner, Button } from "flowbite-react";
import { HiX } from 'react-icons/hi';
import { Route, Routes } from "react-router-dom";
import Home from "./pages/Home";
import About from "./pages/About";
import Contribute from "./pages/Contribute";

const App = () => {
  return (
    <div>
      <Banner>
        <div className="hidden flex-col justify-between border-b border-gray-100 bg-white p-3 dark:border-gray-600 dark:bg-gray-700 md:flex md:flex-row">
          <div className="mb-3 mr-4 flex flex-col items-start md:mb-0 md:flex-row md:items-center">
            <p className="suit flex items-center text-sm font-normal text-gray-500 dark:text-gray-400">
              해당 웹사이트에선 양질의 사용자 경험을 위해&nbsp;<a className="underline text-blue-600 hover:text-blue-800 visited:text-purple-600" href="https://clarity.microsoft.com/">Clarity 애널리틱스 툴</a>을 사용하고 있습니다.
              <b>&nbsp;절대로 귀하의 중요한 개인정보를 수집하지 않으니 안심하시기 바랍니다.</b>
            </p>
          </div>
          <div className="flex flex-shrink-0 items-center">
            <Banner.CollapseButton color="gray" className="border-0 bg-transparent text-gray-500 dark:text-gray-400">
              <HiX className="h-4 w-4" />
            </Banner.CollapseButton>
          </div>
        </div>
      </Banner>
      <Navbar fluid rounded className="suit">
        <Navbar.Brand href="/">
          <img
            src="https://cdn.jsdelivr.net/gh/currenjin/site-for-developers/resources/icon_transparent/128x128/icon_transparent.svg"
            className="mr-1 h-8"
            alt="Flowbite React Logo"
          />
          <span className="suit self-center whitespace-nowrap text-xl font-semibold dark:text-white">
            Site For Developers
          </span>
        </Navbar.Brand>
        <Navbar.Toggle />
        <Navbar.Collapse>
          <Navbar.Link href="/" className="rounded-xl">
            메인
          </Navbar.Link>
          <Navbar.Link href="/about" className="rounded-xl">
            소개
          </Navbar.Link>
          <Navbar.Link href="/contribute" className="rounded-xl">
            기여
          </Navbar.Link>
        </Navbar.Collapse>
      </Navbar>
      <div className="m-4">
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
