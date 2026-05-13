import './Profiles.css';
import React, { useState, useEffect } from 'react';

export const Profiles = () => {

  return (
    <div className="profiles-container">
      <button 
        className="profile-button" 
        onClick={() => window.electron.openProfilePage()}
      >
        👤
      </button>
    </div>
  );
};

export const ProfilePage = () => {

  const [users, setProfile] = useState([]);

  useEffect(() => {

    const fetchProfiles = async () => {
      const data = await window.electron.getProfiles(); 
      setProfile(data || []);
    };
    
    fetchProfiles();
  }, []);

  return (
    <div className="profile-page-container">
      <div className="action-bar">
        <button className="rect-btn">Open</button>
        <button className="rect-btn">Add</button>
        <button className="rect-btn">Change Name</button>
        <button className="rect-btn">Delete</button>
      </div>

      <div className="user-list-section">
        <h2>Select User</h2>
        <div className="user-list">
          {users.map((user) => (
            <div key={user.id} className="user-card">
              {user.name}
            </div>
          ))}
          {users.length === 0 && <p>No users found.</p>}
        </div>
      </div>
    </div>
  );
};