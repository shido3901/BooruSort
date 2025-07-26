import sqlite3

class Groups():
    def __init__(self, db):
        self.booru_db = db

    def add_group(self, group_list):
        
        with self.booru_db.conn:
            self.booru_db.cursor.executemany("INSERT OR IGNORE INTO tag_group (parent_tag_id, child_tag_id, direction) VALUES (?, ?, ?)", group_list)

    def delete_tag_group(self, parent_tag_id):

        with self.booru_db.conn:
            self.booru_db.cursor.executemany("DELETE FROM tag_group WHERE parent_tag_id = ?", parent_tag_id)

    def load_group(self):

        self.booru_db.cursor.execute("""
            SELECT parent.name, child.name, direction
            FROM tag_group tg
            JOIN tags parent ON tg.parent_tag_id = parent.id
            JOIN tags child ON tg.child_tag_id = child.id
            WHERE parent.profile_id = ? AND child.profile_id = ?
        """, (self.booru_db.profile_id, self.booru_db.profile_id))
        tag_pairs = self.booru_db.cursor.fetchall()

        print(f"tag pairs{tag_pairs}")

        return tag_pairs