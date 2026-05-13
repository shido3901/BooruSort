import Database from 'better-sqlite3'
import path from 'node:path'
import fs from 'node:fs'
import { app } from 'electron'

let db;

function initDb() {

    const userDataPath = app.getPath('userData')
    const dbPath = path.join(userDataPath, 'media.db')
    const userFolderPath = path.join(userDataPath, 'User')
   
    let newProfile = false; 

    if (!fs.existsSync(userFolderPath)) {
        fs.mkdirSync(userFolderPath, { recursive: true })
        
        newProfile = true
    }
    
    db = new Database(dbPath);
    
    const createTables = db.transaction(() => {

        db.prepare(`
            CREATE TABLE IF NOT EXISTS profile (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL
            )
        `).run()

        db.prepare(`
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            )
        `).run()

        db.prepare(`
            CREATE TABLE IF NOT EXISTS media (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT,
                path TEXT NOT NULL,
                length TEXT,
                date TEXT
            )
        `).run()
    });

    createTables();
    console.log("Database initialized at ", dbPath);


    if (newProfile) {
        console.log("Creating profile")
        const stmt = db.prepare('INSERT OR IGNORE INTO profile (name) VALUES (?)')

        stmt.run("User")
        
        console.log("Boolean check passed: Added default 'User' to profile table.")
    }

    return db
}

export { initDb, db }

export function getProfiles() {

  try {
    return db.prepare('SELECT * FROM profile').all()
  } catch (err) {
    console.error("Failed to fetch profiles:", err)
    return [];
  }
}

export function addProfile(name) {

  try {
    const stmt = db.prepare('INSERT INTO profile (name) VALUES (?)')
    const info = stmt.run(name)
    
    return { success: true, id: info.lastInsertRowid }
  } catch (err) {
    console.error("Database Error:", err)
    return { success: false, error: err.message }
  }
}

export function deleteProfile(name) {

  try {

    const stmt = db.prepare('DELETE FROM profile WHERE name = ?')
    const info = stmt.run(name)
    
    if (info.changes > 0) {
      return { success: true }
    } else {
      return { success: false, error: "Profile not found." }
    }
  } catch (err) {
    console.error("Database Error:", err)
    return { success: false, error: err.message }
  }
}

const mockTags = [
  { id: 1, name: 'landscape', count: 12 },
  { id: 2, name: 'character', count: 3 },
  { id: 3, name: 'digital art', count: 5 },
  { id: 4, name: 'sketch', count: 82 },
  { id: 5, name: 'wallpaper', count: 23 }
];

export const tagList = () => {
  return mockTags; 
};

