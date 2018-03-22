import mysql.connector
import traceback
class DatabaseManager:
    def __init__(self,host,user,password,port,database,charset='utf8'):
        self.config = {
            'host': host,
            'user': user,
            'password': password,
            'port': port,
            'database': database,
            'charset': 'utf8'
        }
        try:
            self.conn = mysql.connector.connect(**self.config)
        except BaseException, msg:
            print msg
            print 'traceback.format_exc():\n%s' % traceback.format_exc()
    def select(self,sql):
        cursor = self.conn.cursor()
        try:
            cursor.execute(sql)
            return cursor.fetchall()
        except BaseException, msg:
            print msg
            print 'traceback.format_exc():\n%s' % traceback.format_exc()
    def insert(self,sql,data):
        cursor = self.conn.cursor()
        try:
            cursor.execute(sql,tuple(data))
            self.conn.commit()
        except BaseException, msg:
            print msg
            print 'traceback.format_exc():\n%s' % traceback.format_exc()
            self.conn.rollback()
    def insertMany(self,sql,data):
        list = []
        for item in data:
            list.append(tuple(item))
        cursor = self.conn.cursor()
        try:
            cursor.executemany(sql,list)
            self.conn.commit()
        except BaseException, msg:
            print msg
            print 'traceback.format_exc():\n%s' % traceback.format_exc()
            self.conn.rollback()
    def updata(self,sql,data):
        cursor = self.conn.cursor()
        try:
            cursor.execute(sql,tuple(data))
            self.conn.commit()
        except BaseException, msg:
            print msg
            print 'traceback.format_exc():\n%s' % traceback.format_exc()
            self.conn.rollback()
