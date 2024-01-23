import '../components/css/pages.home.css';
import axios from "axios";
import { marked } from "marked";
import { gfmHeadingId } from "marked-gfm-heading-id";
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
    .get("https://raw.githubusercontent.com/currenjin/site-for-developers/main/README.md")
    .then((response) => {
      console.log(response.data);
      setmdData(marked.parse(response.data));
    });

    console.log(mdData);
  return (
    <div>
      <div
        className="mddata ml-4 mr-4 mb-4 p-4 rounded-lg bg-base-200 pretendard text-wrap"
        dangerouslySetInnerHTML={{ __html: mdData }}
      ></div>
    </div>
  );
};

export default Home;
