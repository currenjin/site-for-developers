import "../components/css/pages.home.css";
import axios from "axios";
import { marked } from "marked";
import { gfmHeadingId } from "marked-gfm-heading-id";
import { useState, React } from "react";

const Home = () => {
  const [mdData, setMdData] = useState([]);

  const options = {
    prefix: "",
  };

  marked.use(
    {
      gfm: true,
    },
    gfmHeadingId(options)
  );

  axios
    .get(
      "https://raw.githubusercontent.com/currenjin/site-for-developers/main/README.md"
    )
    .then((response) => {
      console.log(response.data);
      setMdData(marked.parse(response.data));
    });

  console.log(mdData);
  return (
    <div>
      <div
        className="home p-2 rounded-lg border-2"
        dangerouslySetInnerHTML={{ __html: mdData }}
      ></div>
    </div>
  );
};

export default Home;
