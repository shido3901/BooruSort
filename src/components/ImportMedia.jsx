import './ImportMedia.css'
import React, { useState, useEffect } from 'react'

export const ImportMedia = ({ setPage }) => {
    return (
        <div className="media-container">
            <button className="media-button" onClick={() => setPage('import-page')}>import</button>
        </div>
    );
};

export const ImportMediaView = () => {
  return (
    <div className="import-box-container">
      <div className="white-box">
     
        <p>drag media here</p>
      </div>
    </div>
  )
}