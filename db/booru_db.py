import sqlite3
from config.profile_config import CategoryManager
from config.ui_config import MessageBox

from db.tags import Tags
from db.categories import Categories
from db.groups import Groups
from db.pairs import Pairs
from db.files import Files


class BooruDb():
    def __init__(self, db_name="db/booru.db", main_window=None):

        self.db_name = db_name        
        self.main_window = main_window
        
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()

        self.current_profile = None
        self.cursor.execute("PRAGMA foreign_keys = ON")

        self.create_tables() #Remember to do double check this

    def initClass(self):

        self.tags = Tags(db=self)
        self.categories = Categories(db=self)
        self.groups = Groups(db=self)
        self.pairs = Pairs(db=self)
        self.files = Files(db=self)

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
            CREATE TABLE IF NOT EXISTS tag_group (
                parent_tag_id INTEGER,
                child_tag_id INTEGER,
                direction INTEGER,
                PRIMARY KEY (parent_tag_id, child_tag_id),
                FOREIGN KEY (parent_tag_id) REFERENCES tags(id) ON DELETE CASCADE,
                FOREIGN KEY (child_tag_id) REFERENCES tags(id) ON DELETE CASCADE
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

        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_tag_group_child ON tag_group(child_tag_id)")

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
        
        self.cursor.execute("SELECT category_id, name, color FROM category WHERE profile_id = ?", (self.profile_id,))
        self.category_info = self.cursor.fetchall()
        print(f"category info:{self.category_info}")
      
        self.cat_color_dict = {name: color for _, name, color in self.category_info}

        print(f"cat color dic {self.cat_color_dict}")
       

        self.cat_list = self.category_manager.load_json()

        if self.cat_list is None:
            self.cat_list = self.category_manager.dump_json(self.cat_color_dict)
            print('DUMP NOW')
        else:
            if "tags" in self.cat_list:
                print('tags detected')

        if len(self.category_info) != len(self.cat_list):

            self.cat_list = self.category_manager.dump_json(self.cat_color_dict)
            self.cat_list = self.category_info

            category_mismatch = MessageBox(f"Category mismatch. Category list may be out of order.", "warning", "BooruSort")
            category_mismatch.show()
        else:
            print('synced category list!')

    def set_tag_info(self):

        self.tag_list = {}
        
        self.cursor.execute("""
            SELECT tags.id, tags.name, tags.count, category.name
            FROM tags
            JOIN category_tag ON tags.id = category_tag.tag_id
            JOIN category ON category_tag.category_id = category.category_id
            WHERE category.profile_id = ?
        """, (self.profile_id,))
            
        self.tag_info = self.cursor.fetchall()

        for id, tag_name, tag_count, category_name in self.tag_info:
           
            if category_name in self.cat_list:
                tag_color = self.cat_list[category_name]
         
            self.tag_list[tag_name] = {
                "id": id,
                "color": tag_color,
                "category": category_name,
                "count": tag_count
            }

            tag_list_ids= []

            for tag_name in self.tag_list:
                if tag_name in self.tag_list:
                    tag_id = self.tag_list[tag_name]

                    tag_list_ids.append(tag_id)




        
        #print(f"current tag list is {self.tag_list}")
        self.cursor.execute("SELECT COUNT(*) FROM tags WHERE profile_id = ?", (self.profile_id,))
        self.count = self.cursor.fetchone()[0]

    def set_file_count(self):
       
        self.cursor.execute("SELECT COUNT(*) FROM files WHERE profile_id = ?", (self.profile_id,))
        self.file_count = self.cursor.fetchone()[0]

    def set_window_title(self):
        self.main_window.setWindowTitle(f"BooruSort - {self.current_profile} ({self.get_tag_count()} tags, {self.get_item_count()} items)")

    
    def add_items(self, item_list):

        data = [(path, thumbnail, self.profile_id) for (path, thumbnail) in item_list]
        with self.conn:
            self.cursor.executemany("INSERT INTO files (path, thumbnail_name, profile_id) VALUES (?, ?, ?)", data)


    def delete_profile(self, name):

        pass



    def get_category_count(self, name):
        print("name is", name)

        self.cursor.execute("SELECT category_id FROM category WHERE name = ? AND profile_id = ?", (name, self.profile_id))
        id = self.cursor.fetchone()[0]


        self.cursor.execute("SELECT COUNT(*) FROM category_tag WHERE category_id = ?", (id,))
        count = self.cursor.fetchone()[0]

        return count
        

    def delete_items(slef):
            pass

    def close(self):
        self.conn.close() 

    def update_tag_info(self):
        self.set_tag_info()

    def update_notes_box(self, text, file_path):

        self.cursor.execute("UPDATE files SET notes = ? WHERE path = ? AND profile_id = ?", (text, file_path, self.profile_id))
        self.conn.commit()

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


        
