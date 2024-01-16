import './App.css';
import { useState, React } from 'react';
import { marked } from 'marked';
import axios from 'axios';

const App = () => {
  const [users, setUsers] = useState([]);

  axios.get('https://cdn.jsdelivr.net/gh/currenjin/site-for-developers/README.md')
    .then(response => {
      console.log(marked.parse(response.data));
      setUsers(marked.parse(response.data));
    });
  return (
    <div className="ml-4 mr-4 mb-4 p-4 rounded-lg bg-slate-200">
      {users}
    </div>
  );
}

export default App;
