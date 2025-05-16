import "../components/css/pages.contribute.css";
import { marked } from "marked";
import { gfmHeadingId } from "marked-gfm-heading-id";
import { useState, useEffect } from "react";
const Home = () => {
  const [mdDataContribute, setmdDataContribute] = useState([]);

  const options = {
    prefix: "",
  };

  marked.use(
    {
      gfm: true,
    },
    gfmHeadingId(options)
  );

  useEffect(() => {
    fetch(
      "https://raw.githubusercontent.com/currenjin/site-for-developers/main/HOW-TO-CONTRIBUTE.md"
    )
      .then((response) => response.text())
      .then((data) => {
        setmdDataContribute(marked.parse(data));
      });
  }, []);

  return (
    <div>
      <div
        className="contribute p-4 m-2 rounded-xl border-2 border-gray-300 dark:border-gray-600"
        dangerouslySetInnerHTML={{ __html: mdDataContribute }}
      ></div>
    </div>
  );
};

export default Home;
