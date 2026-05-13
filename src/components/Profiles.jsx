import './Profiles.css'
import React, { useState, useEffect } from 'react'

export const Profiles = () => {

  const openProfilePage = () => {
    window.electron.openProfilePage();
  }

  return (
    <div className="profiles-container">
      <button className="open-profile-button" onClick={openProfilePage}>👤</button>
    </div>
  )
}

export const ProfilePage = () => {
 
  const [profiles, setProfiles] = useState([])
  const [currentProfile, setCurrentProfile] = useState(null)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [newProfileName, setNewProfileName] = useState("")

  useEffect(() => {
    const loadData = async () => {
      const profileList = await window.electron.getProfiles()
      setProfiles(profileList)
    }
    loadData();
  }, [])

  const addProfile = async () => {

    if (!newProfileName.trim()) {
      return;
    }

    const result = await window.electron.addProfile(newProfileName)
    
    if (result.success) {
      const data = await window.electron.getProfiles()
      setProfiles(data)
      setNewProfileName("")
      setIsModalOpen(false)
    } else {
      alert("Could not add:" + result.error)
    }
  }

  const openButton = () => {
    console.log("Opening:", currentProfile.name)
  }

  const addButton = () => {
    setIsModalOpen(true);
  }

  const nameButton = () => {
    return null;
  }

  const deleteButton = async () => {

    if (!currentProfile) {
      return;
    }

    const confirmed = confirm(`Delete "${currentProfile.name}"?`)
    
    if (confirmed) {
      const result = await window.electron.deleteProfile(currentProfile.name)

      if (result.success) {
        
        const data = await window.electron.getProfiles()
        setProfiles(data)
        setCurrentProfile(null)
      } else {
        alert("Could not delete:" + result.error)
      }
    }
  }

  const selectCurrentProfile = (user) => {
    setCurrentProfile(user)
  }

  const textInput = (e) => {
    setNewProfileName(e.target.value)
  }

  const enterKey = (e) => {
    if (e.key === 'Enter') {
      addProfile()
    }
  }

  const closeDialog = () => {
    setIsModalOpen(false)
    setNewProfileName("")
  }

  return (
    <div className="profile-page">
      <div className="button-layout">
        <button className="profile-button" onClick={openButton} disabled={!currentProfile}>Open</button>
        <button className="profile-button" onClick={addButton}>Add</button>
        <button className="profile-button" onClick={nameButton} disabled={!currentProfile}>Change Name</button>
        <button className="profile-button" onClick={deleteButton} disabled={!currentProfile}>Delete</button>
      </div>

      <div className="profile-list-section">
        <h2>Profiles</h2>
        <div className="profile-list">
          {profiles.map((user) => (
          <div 
            key={user.id} 
            className={`active-profile-buttons ${currentProfile?.id === user.id ? 'active' : ''}`}
            onClick={() => selectCurrentProfile(user)}
          >
            {user.name}
          </div>
        ))}
        {profiles.length === 0 && <p className="empty-msg">No profiles found</p>}
      </div>
    </div>

    {isModalOpen && (
      <div className="modal-overlay">
        <div className="confirm-box">
          <h3>Create New Profile</h3>
          <input type="text" autoFocus value={newProfileName} onChange={textInput} onKeyDown={enterKey}/>
          <div className="confirm-button">
            <button className="profile-button" onClick={addProfile}>add</button>
            <button className="profile-button" onClick={closeDialog}>cancel</button>
          </div>
        </div>
      </div>
    )}
    </div>
  )
}