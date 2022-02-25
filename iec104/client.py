import logging, socket, time
import ctypes as c,struct

import traceback

from iec104.define import *
from iec104.asdu import asdu

log = logging.getLogger('IEC104client')

SOCKET_TIMEOUT = 60
RECONNECT_TIME = 2

class iec104_client(object):
	"""docstring for iec104"""
	def __init__(self, host, port):
		self.k = 8
		self.host = host
		self.port = port

	def start(self):
		while True:
			try:
				self.connect()
				self.startdt()
				buf = self.recv()
				if not (isinstance(buf,u_apci) and buf.command=="STARDT_CON"):
					raise Exception("Excepted STARTDT_CON")
				while True:
					buf = self.recv()
					if not (isinstance(buf,i_apci)): continue
					# log.debug(buf.tx,buf.rx)
			except Exception as e:
				log.error(traceback.format_exc())
				log.error(e)
				# raise e
			finally:
				self.sock.close()
				time.sleep(RECONNECT_TIME)
	def on_i_frame(self,recieved_asdu):
		if not isinstance(recieved_asdu,asdu):
			return
		recieved_asdu.dump()

	def connect(self):
		self.tx = 0
		self.rx = 0
		self.i_unack = 0

		self.sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM, proto=socket.IPPROTO_TCP)
		self.sock.settimeout(SOCKET_TIMEOUT)
		self.sock.connect( (self.host, self.port))
		log.info("Connected to {}:{}".format(self.host,self.port))
	
	def send (self, data):
		if not isinstance(data,bytes): raise Exception("Send bytes reqired")
		if (len(data)>253): raise Exception("Data length longer then 253 bytes")
		self.sock.send(b'\x68'+len(data).to_bytes(1,'big')+bytes(data))

	def recv(self):
		buf = self.sock.recv(6)
		log.debug(buf)
		if (buf[0]!=START): 
			log.error("Start signature 0x68 not found")
			return
		if ((buf[2]&0x03)==3): 
			log.debug("Recieved U Frame")
			return u_apci(buf[2:6])
		if ((buf[2]&0x03)==1): 
			log.debug("Recieved S Frame")
			return s_apci(buf[2:6])
		if ((buf[2]&0x01)==0): 
			buf += self.sock.recv(buf[1]-4)
			log.debug("Recieved I Frame")
			self.i_unack+=1
			result = i_apci(buf[2:6])
			self.tx = result.tx
			self.rx = result.rx
			if (self.i_unack+1>=self.k):
				self.acknowledge()
			recieved_asdu = asdu(buf[6:])
			self.on_i_frame(recieved_asdu)
			return result

	def acknowledge(self):
		buf = s_apci(bytes(4))
		buf.rx = self.tx
		self.send(bytes(buf))
		self.i_unack = 0

	def startdt(self):
		self.send(U_FRAME["STARDT_ACT"])

class u_apci(bytearray):
	def __init__(self,value):
		super(u_apci, self).__init__(value)
		if len(value)>0:
			self[0] = self[0] | 3
		self.command = self.get_command()
		pass

	def get_command(self):
		for x in U_FRAME:
			if (self==U_FRAME[x]):
				return x
		return "Unknown"

class s_apci(bytearray):
	def __init__(self,value):
		super(s_apci, self).__init__(value)
		self[0] = self[0] | 1
		pass

	@property
	def rx(self):
		return (self[2]>>1)|(self[3]<<7)
	
	@rx.setter 
	def rx(self, value):
		self[2] = (value<<1)&0xFF
		self[3] = (value>>7)&0xFF

class i_apci(bytearray):
	def __init__(self,value):
		super(i_apci, self).__init__(value)
		self[0] = self[0] >> 1 << 1
	@property
	def tx(self):
		return (self[0]>>1)|(self[1]<<7)
	
	@tx.setter 
	def tx(self, value):
		self[0] = (value<<1)&0xFF
		self[1] = (value>>7)&0xFF

	@property
	def rx(self):
		return (self[2]>>1)|(self[3]<<7)
	
	@rx.setter 
	def rx(self, value):
		self[2] = (value<<1)&0xFF
		self[3] = (value>>7)&0xFF

if __name__ == '__main__':
	pass