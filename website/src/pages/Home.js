import '../css/pages.home.css';
import { marked } from "marked";
import { gfmHeadingId } from "marked-gfm-heading-id";
import axios from "axios";
import { useState, React } from "react";

const Home = () => {
  const [mdData, setmdData] = useState([]);

  const options = {
    prefix: "",
  };

  marked.use({
    gfm: true,
  },
  gfmHeadingId(options),);

  axios
    .get("https://cdn.jsdelivr.net/gh/currenjin/site-for-developers/README.md")
    .then((response) => {
      console.log(marked.parse(response.data));
      setmdData(marked.parse(response.data));
    });

    console.log(mdData);
  return (
    <div>
      <div
        className="mddata ml-4 mr-4 mb-4 p-4 rounded-lg bg-gray-200 pretendard"
        dangerouslySetInnerHTML={{ __html: mdData }}
      ></div>
    </div>
  );
};

export default Home;
