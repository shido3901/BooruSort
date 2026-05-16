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
    db.pragma('foreign_keys = ON');
    
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
                name TEXT NOT NULL,
                profile_id INTEGER,
                count INTEGER DEFAULT 0,
                FOREIGN KEY(profile_id) REFERENCES profile(id) ON DELETE CASCADE,
                UNIQUE(profile_id, name)  
            )
        `).run()

        db.prepare(`
            CREATE TABLE IF NOT EXISTS media (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                profile_id INTEGER,
                path TEXT NOT NULL,
                thumbnail_name TEXT NOT NULL,
                type TEXT NOT NULL,
                length TEXT,
                date TEXT NOT NULL,
                FOREIGN KEY(profile_id) REFERENCES profile(id) ON DELETE CASCADE,
                UNIQUE(profile_id, path)
            )
        `).run()

        db.prepare(`
            CREATE TABLE IF NOT EXISTS file_tags (
                file_id INTEGER,
                tag_id INTEGER,
                PRIMARY KEY(file_id, tag_id),
                FOREIGN KEY(file_id) REFERENCES media(id) ON DELETE CASCADE,
                FOREIGN KEY(tag_id) REFERENCES tags(id) ON DELETE CASCADE
            )
        `).run()

    });

    createTables();
    console.log("Database initialized at ", dbPath);

    //TO DO: Check BOTH User Folder and Db file

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
