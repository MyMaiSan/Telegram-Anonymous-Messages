import sqlite3

class DataBase():
    
    async def create(self):
        
        self.con = sqlite3.connect('./database/users.db')
        self.cur = self.con.cursor()
        self.cur.execute('CREATE TABLE IF NOT EXISTS users(user_id TEXT PRIMARY KEY)')
        self.con.commit()
        
    async def add_user(self, user_id):
        try:
            self.cur.execute(f"INSERT INTO users(user_id) VALUES('{user_id}')")
            self.con.commit()
        except BaseException:
            pass
        
    async def delete_user(self, user_id):
        self.cur.execute(f"DELETE FROM users WHERE user_id = '{user_id}'")
        self.con.commit()
        
    async def select_all(self):
        
        data = []
        
        rows = self.cur.execute('SELECT * FROM users').fetchall()
        
        print(rows)
        for i in rows:
        
            data.append({'user_id': i[0]})
        
    
        return data
    
    
DB = DataBase()