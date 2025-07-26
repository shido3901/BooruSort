import sqlite3

class Tags():
    def __init__(self, db):
        self.booru_db = db


    def add_tags(self, new_tag_list, tag_info, tag_names, category_names):

        with self.booru_db.conn:

            self.booru_db.cursor.executemany("INSERT OR IGNORE INTO tags (profile_id, name, count) VALUES (?, ?, ?)", tag_info)

            self.booru_db.cursor.execute(
                f"SELECT id, name FROM tags WHERE profile_id = ? AND name IN ({','.join(['?']*len(tag_names))})",
                (self.booru_db.profile_id, *tag_names)
                )
            
            tag_ids = {name: tag_id for tag_id, name in self.booru_db.cursor.fetchall()}

            self.booru_db.cursor.execute(
                f"SELECT category_id, name FROM category WHERE profile_id = ? AND name IN ({','.join(['?']*len(category_names))})",
                (self.booru_db.profile_id, *category_names)
            )
            
            category_ids = {}
            
            for cat_id, name in self.booru_db.cursor.fetchall():
                category_ids[name] = cat_id
        
            category_tag_pair = []
            category_priority = {cat: i for i, cat in enumerate(self.booru_db.cat_list.keys())}

            add_count = 0

            for tag_name, category_name in new_tag_list:

                tag_id = tag_ids.get(tag_name)
                category_id = category_ids.get(category_name)
                category_tag_pair.append((category_id, tag_id))

                tag_color = self.booru_db.cat_list[category_name]
            
                if tag_name not in self.booru_db.tag_list:
                    
                    self.booru_db.tag_list[tag_name] = {
                        "id": tag_id,
                        "color": tag_color,
                        "category": category_name,
                        "count": 0
                    }

                    add_count += 1

                else:
                    #sets color on category priority
                    curr_category = self.booru_db.tag_list[tag_name]["category"]
                    priority = category_priority[curr_category]
                
                    curr_priority = category_priority[category_name]
                
                    if curr_priority > priority:
                        self.booru_db.tag_list[tag_name]["color"] = tag_color
                        self.booru_db.tag_list[tag_name]["category"] = category_name

            self.booru_db.count += add_count
            self.booru_db.set_window_title()

            self.booru_db.cursor.executemany("INSERT OR IGNORE INTO category_tag (category_id, tag_id) VALUES (?, ?)", category_tag_pair)
            print('success')

    def delete_tags(self, tag_list):
        
        with self.booru_db.conn:
        
            placeholders = ", ".join(["?"] * len(tag_list))
            query = f"SELECT id FROM tags WHERE name IN ({placeholders})"

            self.booru_db.cursor.execute(query, tag_list)
            tag_ids = [(row[0],) for row in self.booru_db.cursor.fetchall()]

            self.booru_db.cursor.executemany("DELETE FROM tags WHERE id = ?", tag_ids)

            for name in tag_list:
                if name in self.booru_db.tag_list:
                    del self.booru_db.tag_list[name]

            self.count -= len(tag_list)
            self.booru_db.set_window_title()

    def get_tag_id(self, tag_list):

        placeholders = ", ".join(["?"] * len(tag_list))
        query = f"SELECT id, name FROM tags WHERE name IN ({placeholders}) AND profile_id = ?"

        params = tag_list + [self.booru_db.profile_id]
        self.booru_db.cursor.execute(query, params)
        tag_ids = self.booru_db.cursor.fetchall()
        return tag_ids