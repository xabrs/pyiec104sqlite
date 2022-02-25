import logging
import time
from multiprocessing import Process, Queue

from iec104.client import iec104_client
from db_data import db_data

host,port = '192.168.100.4', 2404
QUEUE_RECIEVER_SLEEP = 2 	# seconds
COMMIT_COUNTER = 30 		# 30xQUEUE_RECIEVER_SLEEP seconds
def log_init():
	log = logging.getLogger('test')
	log.setLevel(logging.INFO)
	formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
	#file log
	tofile = logging.FileHandler('test.log','a')
	tofile.setLevel(logging.INFO)
	tofile.setFormatter(formatter)
	#console log
	toconsole = logging.StreamHandler()
	toconsole.setLevel(logging.INFO)
	toconsole.setFormatter(formatter)
	log.addHandler(tofile)
	log.addHandler(toconsole)
	log.info('')
	log.info("New log started")
	return log

log = log_init()

###############################################################################

def queue_data_creator(q):
	client = iec104_client(host,port)
	client.on_i_frame = q.put
	client.start()

###############################################################################

def queue_data_reciever(q):
	db = db_data()
	counter = 0
	counter2 = 0
	day = time.localtime().__getitem__(2)
	while True:
		if not (day == time.localtime().__getitem__(2)):
			db.close()
			log.info("Create new sqlite file")
			db = db_data()
			day = time.localtime().__getitem__(2)
		counter = 0
		buf36 = []
		while not q.empty():
			counter+=1
			asdu = q.get()
			for ioa in asdu.ioa:
				if ioa.TypeId != 36:
					continue
				buf36.append((ioa.addr,str(ioa.time), ioa.value, ioa.quality))
		
		counter2 += 1
		db.put(buf36)
		if (counter2>=COMMIT_COUNTER):
			counter2 = 0
			db.commit()
		time.sleep(QUEUE_RECIEVER_SLEEP)

###############################################################################

if __name__ == '__main__':
	q = Queue()
	creator = Process(target=queue_data_creator, args=(q,))
	reciever = Process(target=queue_data_reciever, args=(q,))
	
	try:
		creator.start()
		reciever.start()
	except Exception as e:
		raise e
	finally:
		q.close()
		q.join_thread()
		creator.join()
		reciever.join()
