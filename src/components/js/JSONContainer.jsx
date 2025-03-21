const JSONContainer = ({ category, title, data, paddingtop = true }) => {

   const categoryData = data[category] || [];

   return (
      <div id={category} className={paddingtop ? "pt-6" : null}>
         <span className="text-3xl text-indigo-600 font-bold">{title}</span>
         {categoryData.map((db) => (
            <div className="my-2 p-4 rounded-2xl border-2 border-indigo-600" key={db.title}>
               <div className="md:flex justify-between">
                  <div>
                     <span className="text-4xl">{db.title}</span><br />
                     <span className="text-xl">{db.content}</span><br />
                     {db.feature?.map((dbfeature) => (
                        <div key={dbfeature} className="badge badge-soft mr-2">{dbfeature}</div>
                     ))}
                  </div>
                  <div className="content-end md:min-w-14">
                     <a href={db.link} target="_blank">웹사이트</a>
                  </div>
               </div>
            </div>
         ))}
      </div>
   )
}

export default JSONContainer;