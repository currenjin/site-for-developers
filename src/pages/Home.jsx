import { useEffect, useState } from "react";
import JSONContainer from "../components/js/JSONContainer";
import Index from "../components/js/Index";
import IndexData from "../components/data/index.json";

const Home = ({ searchInput }) => {
  const [data, setData] = useState({});
  const [filteredByCategory, setFilteredByCategory] = useState({});
  const [totalCount, setTotalCount] = useState(0);

  useEffect(() => {
    if (Object.keys(data).length === 0) {
      fetch("https://cdn.jsdelivr.net/gh/currenjin/site-for-developers/data.json")
        .then(response => response.json())
        .then(data => {
          setData(data);
        });
    }

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
      <aside className="md:block hidden fixed h-fit w-68 mx-2 p-3 rounded-xl border-2 border-gray-300 dark:border-gray-600">
        <Index />
      </aside>

      <main className="md:ml-73 w-auto mb-2">
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
