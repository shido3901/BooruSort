import './index.css'
import Searchbar from './components/Searchbar.jsx'
import { createRoot } from 'react-dom/client'
import { Profiles, ProfilePage } from './components/Profiles.jsx'
import { ImportMedia } from './components/ImportMedia.jsx'
import React, { useState } from 'react';

const App = () => {

  const isProfileWindow = window.location.hash === '#profiles'
  const [currentPage, setCurrentPage] = useState('view-media') //uses setPage for middle panel e.g setPage('import-page')

  if (isProfileWindow) {
    return <ProfilePage />
  }

  return (
    <div className="app">
      <div className="left-panel">
        <div className="panel top-left"><Profiles /></div>
          
        <div className="panel bottom-left"></div>
      </div>
      <div className="right-panel">
        <div className="panel top-right">
          <ImportMedia setPage={setCurrentPage} />
          <Searchbar />
         </div>
        <div className="panel middle-right" id="middle-panel">
          {currentPage === 'view-media' && <div className="images">display media</div>}
          {currentPage === 'import-page' && <div className="white-box">import media</div>}
        </div>
        <div className="panel bottom-right"></div>
      </div>
    </div>
  );
};

const container = document.getElementById("root");
const root = createRoot(container);

root.render(<App />);