import { useEffect, useState } from "react";
import JSONContainer from "../components/js/JSONContainer";
import Index from "../components/js/Index";
import IndexData from "../components/data/index.json";
import axios from "axios";

const Home = ({ searchInput }) => {
  const [data, setData] = useState({});
  const [filteredByCategory, setFilteredByCategory] = useState({});
  const [totalCount, setTotalCount] = useState(0);

  useEffect(() => {
    axios
      .get("https://cdn.jsdelivr.net/gh/currenjin/site-for-developers/data.json")
      .then((response) => {
        setData(response.data);
      });
  }, []);

  useEffect(() => {
    if (!data || Object.keys(data).length === 0) return;

    let total = 0;
    const filtered = {};

    IndexData.forEach(({ id }) => {
      const categoryItems = data[id] || [];

      const matches = categoryItems.filter(item => {  
        if (!searchInput) return true;
        const title = item.title?.toLowerCase() || "";
        const content = item.content?.toLowerCase() || "";
        return title.includes(searchInput.toLowerCase()) || content.includes(searchInput.toLowerCase());
      });

      if (matches.length > 0) {
        filtered[id] = matches;
        total += matches.length;
      }
    });

    setFilteredByCategory(filtered);
    setTotalCount(total);
  }, [searchInput, data]);

  return (
    <div>
      <aside className="md:block hidden fixed h-fit w-68 mx-2 p-3 rounded-2xl border border-indigo-600">
        <Index />
      </aside>

      <main className="md:ml-73 w-auto mb-2">
        <div className="md:hidden dropdown dropdown-top dropdown-end fixed bottom-2 right-2">
          <button tabIndex={0} className="btn btn-ghost bg-indigo-600 text-xl text-white min-w-18 h-12 rounded-2xl m-2 border">목차</button>
          <ul tabIndex={0} className="dropdown-content bg-base-100 rounded-2xl z-1 w-60 mr-2 p-2 border-indigo-600 border-2">
            <Index />
          </ul>
        </div>

        {searchInput && totalCount === 0 && (
          <p className="text-center text-black text-xl py-5">검색 결과가 없습니다</p>
        )}

        {IndexData.map(({ id, title }) => (
          filteredByCategory[id] && (
            <JSONContainer
              key={id}
              category={id}
              title={title}
              data={filteredByCategory[id]}
            />
          )
        ))}
      </main>
    </div>
  );
};

export default Home;
