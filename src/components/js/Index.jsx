import IndexData from "../data/index.json";

const Index = () => {
   const indexStyle = "badge border-none bg-indigo-600 text-white m-0.5"

   return (
      <div>
         {IndexData.map((index) => (
            <a href={"#" + index.id} key={index.id}>
               <div className={indexStyle}>{index.name}</div>
            </a>
         ))}
      </div>
   )
}

export default Index;