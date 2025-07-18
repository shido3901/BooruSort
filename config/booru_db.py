import sqlite3
from config.profile_config import CategoryManager
from config.ui_config import MessageBox

class BooruDb():
    def __init__(self, db_name="booru.db", main_window=None):

        self.db_name = db_name
        self.main_window = main_window

        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()

        self.current_profile = None
        self.cursor.execute("PRAGMA foreign_keys = ON")


        self.create_tables() #Remember to do double check this

    def create_tables(self):

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS profiles (
                id INTEGER PRIMARY KEY,
                profile_name TEXT UNIQUE NOT NULL
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS category (
                category_id INTEGER PRIMARY KEY,
                profile_id INTEGER,
                name TEXT NOT NULL,
                color TEXT NOT NULL,
                FOREIGN KEY(profile_id) REFERENCES profiles(id) ON DELETE CASCADE
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY,
                profile_id INTEGER,
                name TEXT UNIQUE NOT NULL, 
                count INTEGER,
                FOREIGN KEY(profile_id) REFERENCES profiles(id) ON DELETE CASCADE
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY,
                profile_id INTEGER,
                path TEXT UNIQUE NOT NULL,
                thumbnail_name TEXT NOT NULL,
                type TEXT NOT NULL,
                length TEXT,
                date TEXT NOT NULL,
                notes TEXT,
                FOREIGN KEY(profile_id) REFERENCES profiles(id)
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS file_tags (
                file_id INTEGER,
                tag_id INTEGER,
                PRIMARY KEY(file_id, tag_id),
                FOREIGN KEY(file_id) REFERENCES files(id),
                FOREIGN KEY(tag_id) REFERENCES tags(id) ON DELETE CASCADE
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS category_tag (
                category_id INTEGER,
                tag_id INTEGER,
                PRIMARY KEY(category_id, tag_id),           
                FOREIGN KEY(category_id) REFERENCES category(category_id) ON DELETE CASCADE,
                FOREIGN KEY(tag_id) REFERENCES tags(id) ON DELETE CASCADE
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS tag_pairs (
                tag_id INTEGER,
                pair_id INTEGER,
                name TEXT,
                PRIMARY KEY(tag_id, pair_id),
                FOREIGN KEY(tag_id) REFERENCES tags(id) ON DELETE CASCADE
            )
        """)

        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_tags_profile_id ON tags(profile_id)")
        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_category_profile_id ON category(profile_id)")

        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_category_tag_tag_id ON category_tag(category_id)")
        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_category_tag_category_id ON category_tag(tag_id)")

        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_file_tags_tag_id ON file_tags(tag_id)")
        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_file_tags_file_id ON file_tags(file_id)")

        self.conn.commit()

    def get_profile_list(self):

        self.cursor.execute("SELECT profile_name FROM profiles")
        profile_list = [row[0] for row in self.cursor.fetchall()]
        return profile_list
       
    def set_curr_profile(self, name):

       if self.current_profile != name:
            self.current_profile = name
            self.category_manager = CategoryManager(self.current_profile)
    
            if name is not None:

                
                self.profile_id = self.get_profile_id()
                self.load_info()

    def get_curr_profile(self):
        return self.current_profile
                   
    def get_profile_id(self):

        self.cursor.execute("SELECT id FROM profiles WHERE profile_name = ?", (self.current_profile,))
        profile = self.cursor.fetchone()
        profile_id = profile[0]
  
        return profile_id
    
    def add_profile(self, name):
        with self.conn:
            self.cursor.execute("INSERT OR IGNORE INTO profiles (profile_name) VALUES (?)", (name,))

            self.current_profile = name
            self.profile_id = self.get_profile_id()

            cat_name = "tags"
            color = "#FFFFFF"
            self.add_category(cat_name, color)
            self.load_info()

    def load_info(self):

        


        self.set_category_list()
        self.set_tag_info()
        self.set_file_count()
        self.set_window_title()

        """print(f"Current profile: {self.current_profile}")
        print(f"Profile ID: {self.profile_id}")
        print(f"Category Info: {self.category_info}")
      
        print(f"Tag Count: {self.count}")
        print(f"File Count: {self.file_count}")"""

    def set_category_list(self):
        
        self.cursor.execute("SELECT name, color FROM category WHERE profile_id = ?", (self.profile_id,))
        category_info = self.cursor.fetchall()
      
        self.cat_color_dict = {name: color for name, color in category_info}
       

        self.cat_list = self.category_manager.load_json()

        if self.cat_list is None:
            self.cat_list = self.category_manager.dump_json(self.cat_color_dict)
            print('DUMP NOW')
        else:
            if "tags" in self.cat_list:
                print('tags detected')

        if len(category_info) != len(self.cat_list):

            self.cat_list = self.category_manager.dump_json(self.cat_color_dict)
            self.cat_list = category_info

            category_mismatch = MessageBox(f"Category mismatch. Category list may be out of order.", "warning", "BooruSort")
            category_mismatch.show()
        else:
            print('synced category list!')

    def set_tag_info(self):

        self.tag_list = {}
        
        self.cursor.execute("""
            SELECT tags.name, tags.count, category.name
            FROM tags
            JOIN category_tag ON tags.id = category_tag.tag_id
            JOIN category ON category_tag.category_id = category.category_id
            WHERE category.profile_id = ?
        """, (self.profile_id,))
            
        self.tag_info = self.cursor.fetchall()

        for tag_name, tag_count, category_name in self.tag_info:
           
            if category_name in self.cat_list:
                tag_color = self.cat_list[category_name]
         
            self.tag_list[tag_name] = {
                "color": tag_color,
                "category": category_name,
                "count": tag_count
            }

        
        #print(f"current tag list is {self.tag_list}")
        self.cursor.execute("SELECT COUNT(*) FROM tags WHERE profile_id = ?", (self.profile_id,))
        self.count = self.cursor.fetchone()[0]

    def set_file_count(self):
       
        self.cursor.execute("SELECT COUNT(*) FROM files WHERE profile_id = ?", (self.profile_id,))
        self.file_count = self.cursor.fetchone()[0]

    def set_window_title(self):
        self.main_window.setWindowTitle(f"BooruSort - {self.current_profile} ({self.get_tag_count()} tags, {self.get_item_count()} items)")

    def add_category(self, name, color, new_list):
        with self.conn:

            self.cursor.execute("INSERT INTO category (profile_id, name, color) VALUES (?, ?, ?)", (self.profile_id, name, color))

            self.cat_list = self.category_manager.dump_json(new_list)

            self.set_category_list()

    def add_tags(self, tag_list):

        with self.conn:
        
            tag_info = [(self.profile_id, tag_name, 0) for tag_name, _ in tag_list]
            self.cursor.executemany("INSERT OR IGNORE INTO tags (profile_id, name, count) VALUES (?, ?, ?)", tag_info)
            
            tag_names = [tag_name for tag_name, _ in tag_list]
            self.cursor.execute(
                f"SELECT id, name FROM tags WHERE profile_id = ? AND name IN ({','.join(['?']*len(tag_names))})",
                (self.profile_id, *tag_names)
                )
            
            tag_ids = {name: tag_id for tag_id, name in self.cursor.fetchall()}
        
            category_names = list(set(cat for _, cat in tag_list))

            self.cursor.execute(
                f"SELECT category_id, name FROM category WHERE profile_id = ? AND name IN ({','.join(['?']*len(category_names))})",
                (self.profile_id, *category_names)
            )
            
            category_ids = {}
            
            for cat_id, name in self.cursor.fetchall():
                category_ids[name] = cat_id
        
            category_tag_pair = []
            category_priority = {cat: i for i, cat in enumerate(self.cat_list.keys())}

            add_count = 0

            for tag_name, category_name in tag_list:

                tag_id = tag_ids.get(tag_name)
                category_id = category_ids.get(category_name)
                category_tag_pair.append((category_id, tag_id))

                tag_color = self.cat_list[category_name]
            
                if tag_name not in self.tag_list:
                    self.tag_list[tag_name] = {
                        "color": tag_color,
                        "category": category_name,
                        "count": 0
                    }

                    add_count += 1


                else:
                    #sets color on category priority
                    curr_category = self.tag_list[tag_name]["category"]
                    priority = category_priority[curr_category]
                
                    curr_priority = category_priority[category_name]
                
                    if curr_priority > priority:
                        self.tag_list[tag_name]["color"] = tag_color
                        self.tag_list[tag_name]["category"] = category_name

            self.count += add_count
            self.set_window_title()

            self.cursor.executemany("INSERT OR IGNORE INTO category_tag (category_id, tag_id) VALUES (?, ?)", category_tag_pair)

    def add_items(self, item_list):

        data = [(path, thumbnail, self.profile_id) for (path, thumbnail) in item_list]
        with self.conn:
            self.cursor.executemany("INSERT INTO files (path, thumbnail_name, profile_id) VALUES (?, ?, ?)", data)

    def delete_profile(self, name):

        pass



    def delete_category(self, name):

        with self.conn:

            category_id = self.get_category_id(name)

            self.cursor.execute("""
                SELECT tag_id
                FROM category_tag
                GROUP BY tag_id
                HAVING COUNT(*) > 1
            """)
            duplicates = [row[0] for row in self.cursor.fetchall()]

            duplicate_list = [tag_id for tag_id in duplicates]

            self.cursor.execute("SELECT tag_id FROM category_tag WHERE category_id = ?", (category_id,))
            orphan_tag = self.cursor.fetchall()
            
            all_tag_ids = [tag_id for tag_id in orphan_tag]

            orphan_tag_list = [(tag_id, 1) for (tag_id,) in all_tag_ids if tag_id not in duplicate_list]

            print(f"orphan tag list is {orphan_tag_list}")

            if orphan_tag_list:

                self.cursor.executemany("INSERT INTO category_tag (tag_id, category_id) VALUES (?, ?)", orphan_tag_list)

            self.cursor.execute("DELETE FROM category WHERE category_id = ?", (category_id,))

            del self.cat_list[name]
            self.cat_list = self.category_manager.dump_json(self.cat_list)
            self.set_category_list()

    def get_category_count(self, name):
        print("name is", name)

        self.cursor.execute("SELECT category_id FROM category WHERE name = ? AND profile_id = ?", (name, self.profile_id))
        id = self.cursor.fetchone()[0]


        self.cursor.execute("SELECT COUNT(*) FROM category_tag WHERE category_id = ?", (id,))
        count = self.cursor.fetchone()[0]

        return count
        

        

    def delete_tags(self, tag_list):
        
        with self.conn:
        
            placeholders = ", ".join(["?"] * len(tag_list))
            query = f"SELECT id FROM tags WHERE name IN ({placeholders})"

            print(f"taglist: {tag_list}")
            print(f"query: {query}")

            self.cursor.execute(query, tag_list)
            tag_ids = [(row[0],) for row in self.cursor.fetchall()]

            self.cursor.executemany("DELETE FROM tags WHERE id = ?", tag_ids)

            for name in tag_list:
                if name in self.tag_list:
                    del self.tag_list[name]

            self.count -= len(tag_list)
            self.set_window_title()

    def delete_items(slef):
            pass

    def close(self):
        self.conn.close() 

    def update_category_info(self, category_name, new_color, new_list): #variables a little misleading, put notes to keep track
        
        #new_color=self.category_list, category_name=None, new_list=None
        if category_name is None and new_list is None: 
            self.cat_list = self.category_manager.dump_json(new_color)

        #self.category_name, self.current_color, new_list=None

        elif new_list is None: 
            with self.conn:
                self.cursor.execute("UPDATE category SET color = ? WHERE name = ? AND profile_id = ?", (new_color, category_name, self.profile_id))
            
                self.cat_list[category_name] = new_color
                self.cat_list = self.category_manager.dump_json(self.cat_list)

        else:
             with self.conn: 
                #category_name=name, new_list=new_dict, new_color=self.old_name
                self.cursor.execute("UPDATE category SET name = ? WHERE name = ? AND profile_id = ?", (category_name, new_color, self.profile_id))
            
                self.cat_list = self.category_manager.dump_json(new_list)
        
        self.set_category_list()

    def update_tag_info(self):
        self.set_tag_info()

    def update_notes_box(self, text, file_path):

        self.cursor.execute("UPDATE files SET notes = ? WHERE path = ? AND profile_id = ?", (text, file_path, self.profile_id))
        self.conn.commit()

    def get_category_id(self, category_name):
        self.cursor.execute("SELECT category_id FROM category WHERE name = ?", (category_name,))
        
        result = self.cursor.fetchone()
        category_id = result[0]

        return category_id

    def get_category_info(self):
        return self.cat_list

    def get_tag_info(self):
        return self.tag_list
    
    def get_tag_count(self):
        return self.count
    
    def get_item_info(self, file_path):

        print('HELLO?')
        self.cursor.execute("SELECT id, path, type, length, date, notes FROM files WHERE path = ?", (file_path,))
        result = self.cursor.fetchone()

        return result
    
    def get_file_tag_info(self, file_path):

        self.cursor.execute("""
            SELECT tags.id, tags.name, tags.count
            FROM files
            JOIN file_tags ON files.id = file_tags.file_id
            JOIN tags ON file_tags.tag_id = tags.id
            WHERE files.path = ?
        """, (file_path,))

        return self.cursor.fetchall()
    
    def load_items(self, tag_names):
            
            get_tags = ','.join(['?'] * len(tag_names))
            query = f"SELECT id FROM tags WHERE name IN ({get_tags}) AND profile_id = ?"

            params = tag_names + [self.profile_id]
            self.cursor.execute(query, params)
            tag_ids = self.cursor.fetchall()

            tag_ids_flat = [row[0] for row in tag_ids]

            placeholders = ','.join(['?'] * len(tag_ids_flat))
            query = (f"SELECT file_id FROM file_tags WHERE tag_id IN ({placeholders}) GROUP BY file_id HAVING COUNT(DISTINCT tag_id) = ?")

            params = tag_ids_flat + [len(tag_ids_flat)]
            self.cursor.execute(query, params)
            file_ids = self.cursor.fetchall()

            file_id_list = [row[0] for row in file_ids]

            placeholders = ",".join("?" for _ in file_id_list)
            self.cursor.execute(f"SELECT path, thumbnail_name, type FROM files WHERE id IN ({placeholders})", file_id_list)
            self.file_paths_list = self.cursor.fetchall()

            self.entity_count = len(self.file_paths_list)

            print(f"from load items: {self.file_paths_list}")

    def get_item_count(self):
        return self.file_count
        
    def get_duplicate_tags(self):
        return self.duplicate_tags
    
    def refresh_tag_info(self):
        self.set_tag_info()


        
