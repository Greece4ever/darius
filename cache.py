"""
Use a simple sqlite3 db for simply caching things
"""
import sqlite3
import time
import datetime
from typing import Tuple,Optional

class Cache:
    """
    __init__ : method,\n (filename : 'Filename Where db will be stored',cache_name : 'Name of Database Table',req_rate : 'Request Rate')
        param: filename (Where the sqlite3 file is saved)
        param: req_rate (Optional : Maximum Number of requests made in a specific interval) (Request Number,Datetime Timedelta)
        param: cache_name (Name of the Database Table)
    save : method
    check : method
    handleTime method
        param: ip (The IP the operations are going to be performed in)
    """
    def __init__(self,filename : str,cache_name : str,req_rate : Tuple[int,datetime.datetime]):
        self.connection = sqlite3.connect(filename)
        self.cachename = cache_name
        self.cursor = self.connection.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS {} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ip text,
                last_check integer,
                checks integer
            )
        """.format(self.cachename))
        self.connection.commit()
        self.rate = req_rate 

    def save(self,ip,cac_val : Optional[int] = None):
        """Cache the IP at the moment the function is called"""
        isCached = self.check(ip).fetchall()
        if not len(isCached) == 0:
            if cac_val is None:
                cac_val : int = isCached[0][-1] + 1
            self.cursor.execute("""
            UPDATE {}
            SET last_check = ?, checks = ?
            WHERE ip = ?
            """.format(self.cachename),(time.time(),cac_val,ip))
        else:
            self.cursor.execute("""
                INSERT INTO {} VALUES (null,?,?,?)
            """.format(self.cachename),(ip,time.time(),1))
        return self.connection.commit()

    def check(self,ip):
        """Check the cache for values on a specific IP"""
        query = self.cursor.execute("""
            SELECT * FROM {}
            WHERE ip = ?
        """.format(self.cachename),(ip,))
        return query

    def handleTime(self,ip):
        beg_data = self.check(ip).fetchall()[0]
        time_since_last_commit = datetime.datetime.now() - datetime.datetime.fromtimestamp(beg_data[-2]) #timedelta
        print(f'Minimum time required : {self.rate[1]}')
        print(f'Time Passed since last : {time_since_last_commit}')
        if time_since_last_commit < self.rate[1]: #if the time interval since the last request has not passed
            if beg_data[-1] > self.rate[0]:
                return "Connection Blocked" # Suitable for 429 Status
            return "Connection OK"
        self.save(ip,0) #Set The Connection Attempts to 0
        return "Connection OK"


if __name__ == "__main__":
    cache = Cache("cache.sqlite3",'Cache',(3,datetime.timedelta(seconds=10)))
    cache.save("192.168.1.1")

    for i in range(10):
        print(cache.handleTime("192.168.1.1"))  
        cache.save("192.168.1.1")
        print(cache.check("192.168.1.1").fetchall()[0])
        input("Continue : ")