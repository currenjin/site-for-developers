import axios from "axios";
import { useEffect, useState } from "react";

const JSONContainer = ({category, title, paddingtop}) => {
   const [data, setData] = useState([]);

   useEffect(() => {
      axios
         .get(
            "https://cdn.jsdelivr.net/gh/currenjin/site-for-developers/data.json"
         )
         .then((response) => {
            setData(response.data);
         });
   }, []);

   const categoryData = data[category] || [];

   return (
      <div>
         <div id={category} className={ paddingtop ? "pt-6" : null }>
            <span className="text-3xl text-indigo-600 font-bold">{title}</span>
            {categoryData.map((db) => (
               <div className="my-2 p-4 rounded-lg border-2 border-indigo-600" key={db.title}>
                  <div className="md:flex justify-between">
                     <div>
                        <span className="text-4xl">{db.title}</span><br />
                        <span className="text-xl">{db.content}</span><br />
                        {db.feature?.map((ecfeature) => (
                           <div key={ecfeature} className="badge badge-soft mr-2">{ecfeature}</div>
                        ))}
                     </div>
                     <div className="content-end md:min-w-15">
                        <a href={db.link} target="_blank">웹사이트</a>
                     </div>
                  </div>
               </div>
            ))}
         </div>
      </div>
   )
}

export default JSONContainer;