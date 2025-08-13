from config.booru_ui import notification_message as notify

class Tags():
    def __init__(self, db):
        self.db = db

    def add_tag(self, new_tag_list, tag_info, tag_names, category_names):

        self.db.cursor.executemany("INSERT OR IGNORE INTO tags (profile_id, name, count) VALUES (?, ?, ?)", tag_info)

        self.db.cursor.execute(
            f"SELECT id, name FROM tags WHERE profile_id = ? AND name IN ({','.join(['?']*len(tag_names))})",
            (self.db.profile_id, *tag_names)
            )
        
        
        tag_ids = {name: tag_id for tag_id, name in self.db.cursor.fetchall()}

        self.db.cursor.execute(
            f"SELECT category_id, name FROM category WHERE profile_id = ? AND name IN ({','.join(['?']*len(category_names))})",
            (self.db.profile_id, *category_names)
        )
        
        category_ids = {}

        
        for cat_id, name in self.db.cursor.fetchall():
            category_ids[name] = cat_id

    
        category_tag_pair = []
        category_priority = {cat: i for i, cat in enumerate(self.db.category_list.keys())}

        add_count = 0

        for tag_name, category_name in new_tag_list:

            tag_id = tag_ids.get(tag_name)
            category_id = category_ids.get(category_name)
            category_tag_pair.append((category_id, tag_id))

            tag_color = self.db.category_list[category_name]
        
            if tag_name not in self.db.tag_list:
                
                self.db.tag_list[tag_name] = {
                    "id": tag_id,
                    "color": tag_color,
                    "category": category_name,
                    "count": 0
                }

                add_count += 1

            else:
                #sets color on category priority
                curr_category = self.db.tag_list[tag_name]["category"]
                priority = category_priority[curr_category]
            
                curr_priority = category_priority[category_name]
            
                if curr_priority > priority:
                    self.db.tag_list[tag_name]["color"] = tag_color
                    self.db.tag_list[tag_name]["category"] = category_name

        self.db.count += add_count
        self.db.set_window_title()

        self.db.cursor.executemany("INSERT OR IGNORE INTO category_tag (category_id, tag_id) VALUES (?, ?)", category_tag_pair)
        notify(f"successfully added {add_count}")