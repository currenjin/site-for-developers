const JSONContainer = ({ category, title, data }) => {
   return (
     <section id={category}>
       <h2 className="text-3xl font-bold md:py-3 py-2 px-1 text-indigo-600">{title}</h2>
       <ul className="grid md:grid-cols-2 grid-cols-1 gap-3">
         {data.map((item, index) => (
           <li key={index} className="p-5 border border-indigo-600 rounded-2xl">
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
