import IndexData from "../data/index.json";

const Index = () => {
   const indexStyle = "badge border-2 border-gray-300 dark:border-gray-600 m-0.75 transition hover:bg-indigo-600 hover:text-white"

   return (
      <div>
         {IndexData.map((index) => (
            <a href={"#" + index.id} key={index.id}>
               <div className={indexStyle}>{index.title}</div>
            </a>
         ))}
      </div>
   )
}

export default Index;