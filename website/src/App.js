import ReactMarkdown from 'react-markdown';
import style from './markdown-styles.module.css';
import './App.css';
import axios from 'axios';
import { useState } from 'react';
import remarkGfm from 'remark-gfm'

const App = () => {
  const [users, setUsers] = useState([]);

  axios.get('https://cdn.jsdelivr.net/gh/currenjin/site-for-developers/README.md')
    .then(response => {
      console.log(response.data);
      setUsers(response.data);
    });
  return (
    <div className="App">
      <ReactMarkdown remarkPlugins={[remarkGfm]} className={style.reactMarkDown}>
        {"'"+

        users

        +"'"}
      </ReactMarkdown>
    </div>
  );
}

export default App;