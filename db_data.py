import sqlite3
from db import db

import time

def get_todayfilename():
	return time.strftime("%Y%m%d.sqlite")

class db_data(db):
	"""docstring for db_data"""

	def __init__(self, filename=None):
		if not isinstance(filename,str):
			filename = get_todayfilename()
		super(db_data, self).__init__(filename,"data_create.sqlite")

	def put(self,buf):
		if (len(buf)==0): 
			return
		cursor = self.sql.cursor()

		for (addr, dt, v, q) in buf:
			query = f'INSERT INTO data (id, dt, v, q) VALUES ({addr}, "{dt}", {v}, {q});'
			try:
				cursor.executescript(query)
			except sqlite3.IntegrityError as e:
				log.error(e)
			except Exception as e:
				log.error(e)
		cursor.close()

