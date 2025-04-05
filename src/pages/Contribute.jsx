import "../components/css/pages.contribute.css";
import { marked } from "marked";
import { gfmHeadingId } from "marked-gfm-heading-id";
import axios from "axios";
import { useState } from "react";

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

  axios
    .get(
      "https://raw.githubusercontent.com/currenjin/site-for-developers/main/HOW-TO-CONTRIBUTE.md"
    )
    .then((response) => {
      console.log(response.data);
      setmdDataContribute(marked.parse(response.data));
    });

    console.log(mdDataContribute);
    return (
        <div>
            <div
                className="contribute p-3 m-2 rounded-2xl border border-indigo-600"
                dangerouslySetInnerHTML={{__html: mdDataContribute}}
            ></div>
        </div>
    );
};

export default Home;
