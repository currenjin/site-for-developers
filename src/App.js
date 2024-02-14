import "./components/css/App.css";
import { React } from "react";
import { Navbar } from "flowbite-react";
import { Route, Routes, Link } from "react-router-dom";
import Home from "./pages/Home";
import About from "./pages/About";
import Contribute from "./pages/Contribute";

const App = () => {
  return (
    <div>
      <Navbar fluid rounded className="suit">
        <Navbar.Brand href="/">
          <img
            src="https://i.ibb.co/x5rw85r/site-for-developers-icon.png"
            className="mr-1 h-9"
            alt="Flowbite React Logo"
          />
          <span className="suit self-center whitespace-nowrap text-xl font-semibold dark:text-white">
            Site For Developers
          </span>
        </Navbar.Brand>
        <Navbar.Toggle />
        <Navbar.Collapse>
          <Navbar.Link href="/" className="rounded-xl">메인</Navbar.Link>
          <Navbar.Link href="/about" className="rounded-xl">소개</Navbar.Link>
          <Navbar.Link href="/contribute" className="rounded-xl">기여</Navbar.Link>
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
