import './Searchbar.css';
import React, { useState, useEffect } from 'react';

const Searchbar = () => {
    
  const [tagListSearch, setTagListSearch] = useState("");
  const [filteredTags, setFilteredTags] = useState([]);

  useEffect(() => {
    const fetchTags = async () => {
      const query = tagListSearch.trim();

      if (query !== "") {
        try {
    
          const results = await window.electron.getTags(query);
          
          setFilteredTags(Array.isArray(results) ? results : []);
        } catch (error) {
          console.error("Database query failed:", error);
          setFilteredTags([]);
        }
      } else {
        setFilteredTags([]);
      }
    };

    // This runs every time the user types
    fetchTags();
  }, [tagListSearch]);

  
    return (
    <div className="search-bar">
        <div className="search-widget">
        <input
            type="text"
            className="search-input"
            value={tagListSearch}
            onChange={(e) => setTagListSearch(e.target.value)}
        />
        <button className="search-button">🔍</button>
        </div>

        {filteredTags.length > 0 && (
        <div className="search-dropdown">
            {filteredTags.map((tag) => (
            <div key={tag.id} className="tag-result" onClick={() => console.log(tag.name)}>
                <span className="tag-name">{tag.name}</span>
            </div>
            ))}
        </div>
        )}
    </div>
    );
};

export default Searchbar;