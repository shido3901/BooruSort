import './ImportMedia.css'
import React, { useState, useEffect, useRef } from 'react'

export const ImportMediaButton = ({ setPage }) => {
    return (
        <div className="media-container">
            <button className="media-button" onClick={() => setPage('import-page')}>import</button>
        </div>
    )
}

export const ImportMediaPage = () => {

  const fileInputRef = useRef(null)

  const dragMedia = (e) => {
    e.preventDefault();
  }

  const dropMedia = (e) => {
    e.preventDefault();
    const files = Array.from(e.dataTransfer.files)
    checkMedia(files)
  }

  const clickMedia = (e) => {
    const files = Array.from(e.target.files)
    checkMedia(files)
  }

  const checkMedia = (files) => {
    files.forEach(file => {
      if (file.type.startsWith('image/') || file.type.startsWith('video/')) {

        console.log("File Name:", file.name)
        const absolutePath = window.electron.getFilePath(file)
        console.log("File path at:", absolutePath)

      } else {
        alert("File not supported")
      }
    })
  }

  const handleBoxClick = () => {
    
    fileInputRef.current.click()
  }

  const currentTagList = useRef(null)

  const ImportMedia = () => {

    const finalTagList = currentTagList.current.value
      .split(/\s+/)
      .map(tag => tag.trim())
      .filter(tag => tag !== '')

    console.log("importing tags:", finalTagList)
    
  }

  return (
    <div className="import-box-container">
      
      <input 
        type="file" 
        ref={fileInputRef} 
        style={{ display: 'none' }} 
        multiple 
        accept="image/*,video/*"
        onChange={clickMedia}
      />
    
      <div 
        className="import-box"
        onDragOver={dragMedia}
        onDrop={dropMedia}
        onClick={handleBoxClick}
      >
        <p>drag media here </p>
        <p>or click to browse</p>
      </div>

      <div className="import-area">
        <textarea
          ref={currentTagList}
          type="text"
          className="tag-box" 
          placeholder="enter tags (e.g. nature, cute_cat)"
          spellCheck="false"
        />
        <button 
          className="import-media" onClick={ImportMedia}>+</button>
      </div>
    </div>
  )
}