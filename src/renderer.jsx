import './index.css';
import Searchbar from './components/Searchbar.jsx';
import { createRoot } from 'react-dom/client';
import { Profiles, ProfilePage } from './components/Profiles.jsx';

const App = () => {

  const isProfileWindow = window.location.hash === '#profiles';

  if (isProfileWindow) {
    return <ProfilePage />;
  }

  return (
    <div className="app">
      <div className="left-panel">
        <div className="panel top-left"><Profiles /></div>
          
        <div className="panel bottom-left"></div>
      </div>
      <div className="right-panel">
        <div className="panel top-right"><Searchbar /> </div>
        <div className="panel middle-right" id="middle-panel"></div>
        <div className="panel bottom-right"></div>
      </div>
    </div>
  );
};

const container = document.getElementById("root");
const root = createRoot(container);

root.render(<App />);