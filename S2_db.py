# (A) SQLITE & DATABASE FILE
# S2_db.py
import sqlite3
DB_FILE = "sql.db"

# (B) SAVE INTO DATABASE
def save(name, mime, data, ids):
  conn = sqlite3.connect(DB_FILE)
  cursor = conn.cursor()
  cursor.execute(
    "REPLACE INTO `profileimage` (`file_name`, `file_mime`, `file_data`, `userid`) VALUES (?,?,?,?)",
    (name, mime, data,ids)
  )
  conn.commit()
  conn.close()

def get_user_by_id(user_id):
  conn = sqlite3.connect(DB_FILE)
  cursor = conn.cursor()
  query = "SELECT * FROM profileimage WHERE userid = ?"
  cursor.execute(query, (user_id,))
  user = cursor.fetchone()
  return user