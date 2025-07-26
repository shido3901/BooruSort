class Files():
    def __init__(self, db):
        self.booru_db = db

    def load_file_info(self, tag_names):

        tag_ids = [self.booru_db.tag_list[name]["id"] for name in tag_names if name in self.booru_db.tag_list]

        placeholders = ','.join(['?'] * len(tag_ids))
        query = (f"SELECT file_id FROM file_tags WHERE tag_id IN ({placeholders}) GROUP BY file_id HAVING COUNT(DISTINCT tag_id) = ?")
        values = tag_ids + [len(tag_ids)]

        self.booru_db.cursor.execute(query, values)
        file_ids = self.booru_db.cursor.fetchall()

        file_id_list = [row[0] for row in file_ids]

        placeholders = ",".join("?" for _ in file_id_list)
        self.booru_db.cursor.execute(f"SELECT path, thumbnail_name, length, type FROM files WHERE id IN ({placeholders})", file_id_list)
        file_paths_list = self.booru_db.cursor.fetchall()

        return file_paths_list
