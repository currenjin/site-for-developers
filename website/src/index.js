import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <div className="navbar bg-base-100">
      <div className="flex-none">
      </div>
      <div className="flex-1">
        <a className="btn btn-ghost text-xl suit">💎 Site for developers</a>
      </div>
      <div className="flex-none">
      </div>
    </div>
    <App />
  </React.StrictMode>
);
