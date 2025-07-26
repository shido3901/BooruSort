import sqlite3

class Categories():
    def __init__(self, db):
        self.booru_db = db

    def add_category(self, name, color, new_list):
        with self.booru_db.conn:

            self.booru_db.cursor.execute("INSERT INTO category (profile_id, name, color) VALUES (?, ?, ?)", (self.booru_db.profile_id, name, color))
            self.booru_db.cat_list = self.booru_db.category_manager.dump_json(new_list)
            self.booru_db.set_category_list()

    def delete_category(self, name):

        with self.booru_db.conn:

            category_id = next((cat_id for (cat_id, tag_name, _) in self.booru_db.category_info if tag_name == name))

            self.booru_db.cursor.execute("""
                SELECT tag_id
                FROM category_tag
                GROUP BY tag_id
                HAVING COUNT(*) > 1
            """)

            duplicates = [row[0] for row in self.booru_db.cursor.fetchall()]

            duplicate_list = [tag_id for tag_id in duplicates]

            self.booru_db.cursor.execute("SELECT tag_id FROM category_tag WHERE category_id = ?", (category_id,))
            orphan_tag = self.booru_db.cursor.fetchall()
            
            all_tag_ids = [tag_id for tag_id in orphan_tag]

            orphan_tag_list = [(tag_id, 1) for (tag_id,) in all_tag_ids if tag_id not in duplicate_list]

            print(f"orphan tag list is {orphan_tag_list}")

            if orphan_tag_list:

                self.booru_db.cursor.executemany("INSERT INTO category_tag (tag_id, category_id) VALUES (?, ?)", orphan_tag_list)

            self.booru_db.cursor.execute("DELETE FROM category WHERE category_id = ?", (category_id,))

            del self.booru_db.cat_list[name]

            self.booru_db.cat_list = self.booru_db.category_manager.dump_json(self.booru_db.cat_list)
            self.booru_db.set_category_list()

    def get_category_count(self, name):
        print("name is", name)

        self.booru_db.cursor.execute("SELECT category_id FROM category WHERE name = ? AND profile_id = ?", (name, self.booru_db.profile_id))
        id = self.booru_db.cursor.fetchone()[0]


        self.booru_db.cursor.execute("SELECT COUNT(*) FROM category_tag WHERE category_id = ?", (id,))
        count = self.booru_db.cursor.fetchone()[0]

        return count
    
    def update_category_info(self, category_name, new_color, new_list): #variables a little misleading, put notes to keep track
        
        #new_color=self.category_list, category_name=None, new_list=None
        if category_name is None and new_list is None: 
            self.booru_db.cat_list = self.booru_db.category_manager.dump_json(new_color)

        #self.category_name, self.current_color, new_list=None

        elif new_list is None: 
            with self.booru_db.conn:
                self.booru_db.cursor.execute("UPDATE category SET color = ? WHERE name = ? AND profile_id = ?", (new_color, category_name, self.booru_db.profile_id))
            
                self.booru_db.cat_list[category_name] = new_color
                self.booru_db.cat_list = self.booru_db.category_manager.dump_json(self.booru_db.cat_list)

        else:
             with self.booru_db.conn: 
                #category_name=name, new_list=new_dict, new_color=self.old_name
                self.booru_db.cursor.execute("UPDATE category SET name = ? WHERE name = ? AND profile_id = ?", (category_name, new_color, self.profile_id))
            
                self.cat_list = self.booru_db.category_manager.dump_json(new_list)
        
        self.booru_db.set_category_list()
