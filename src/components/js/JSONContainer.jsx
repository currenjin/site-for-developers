import { useEffect, useState } from "react";

const JSONContainer = ({ category, title, data }) => {
  const [favicons, setFavicons] = useState({});

  useEffect(() => {
    const fetchFavicons = async () => {
      const newFavicons = {};

      for (const item of data) {
        if (item.link) {
          const url = new URL(item.link);
          const faviconUrl = `https://www.google.com/s2/favicons?sz=64&domain=${url.origin}`;
          newFavicons[item.link] = faviconUrl;
        }
      }
      setFavicons(newFavicons);
    };

    fetchFavicons();
  }, [data]);

  return (
    <section id={category}>
      <h2 className="text-3xl font-bold md:py-3 py-2 px-1 text-indigo-600">{title}</h2>
      <ul className="md:grid grid-cols-2 gap-3">
        {data.map((item, index) => (
          <li key={index} className="p-4 border-2 border-gray-300 dark:border-gray-600 rounded-xl">
            {favicons[item.link]?.trim() && (
              <img
                src={favicons[item.link]}
                alt={`${item.link} icon`}
                className="rounded-lg mb-1"
                width="30"
                height="30"
                loading="lazy"
              />
            )}
            <a href={item.link} target="_blank" rel="noreferrer" className="text-xl font-semibold text-indigo-600 hover:underline">
              {item.title}
            </a>
            <p className="text-sm mt-1">{item.content}</p>
            <div className="mt-2 flex flex-wrap gap-1">
              {item.feature?.map((feature) => (
                <span key={feature} className="badge badge-soft mr-2">{feature}</span>
              ))}
            </div>
          </li>
        ))}
      </ul>
    </section>
  );
};

export default JSONContainer;
