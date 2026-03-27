import sqlite3
import re
import os

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

class SQLiteConnection:
    def __init__(self, db):
        self.db_path = f"{db}.sqlite"
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = dict_factory
        
    def query_db(self, query, data=None):
        # Convert MySQL parameter format %(name)s to SQLite format :name
        sqlite_query = re.sub(r'%\((.*?)\)s', r':\1', query)
        # Convert MySQL NOW() to SQLite datetime('now')
        sqlite_query = sqlite_query.replace('NOW()', "datetime('now')")
        
        cursor = self.connection.cursor()
        try:
            if data:
                cursor.execute(sqlite_query, data)
            else:
                cursor.execute(sqlite_query)
                
            if sqlite_query.lower().find("insert") >= 0:
                self.connection.commit()
                return cursor.lastrowid
            elif sqlite_query.lower().find("select") >= 0:
                result = cursor.fetchall()
                return result
            else:
                self.connection.commit()
        except Exception as e:
            return False
        finally:
            self.connection.close() 

def connectToMySQL(db):
    return SQLiteConnection(db)
