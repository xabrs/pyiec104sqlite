from struct import unpack
from datetime import datetime
from time import strftime

from iec104.define import *

class CP56Time(datetime):
	"""docstring for CP56Time"""
	def __str__(self):
		return self.strftime("%Y/%m/%d %H:%M:%S.%f")[:-3]
		
def cp56time2a_to_time(buf):
	milliseconds = (buf[1] << 8) | buf[0] 
	second = int(milliseconds/1000)
	microsecond = (milliseconds%1000)*1000
	minute = buf[2] & 0x3F
	hour = buf[3] & 0x1F
	day = buf[4] & 0x1F
	month = (buf[5] & 0x0F)
	year = (buf[6] & 0x7F) + 2000
	return CP56Time(year, month, day, hour, minute, second, microsecond)

def datetime_to_str(dt):
	return strftime("%Y/%m/%d %H:%M:%S.%f",dt.timetuple())

class QUALITY(object):
	def __init__(self, value):
		self.value = value&0xFF

	@property
	def byte(self):
		return self.value
	@byte.setter 
	def byte(self, value):
		self.value = value&0xFF

	@property
	def BL(self):
		return (self.value&0b00010000>0)
	@BL.setter 
	def BL(self, value):
		if (value):
			self.value = self.value|0b00010000
		else:
			self.value = self.value&0b11101111
		return self.value
	
	@property
	def SB(self):
		return (self.value&0b00100000>0)
	@SB.setter 
	def SB(self, value):
		if (value):
			self.value = self.value|0b00100000
		else:
			self.value = self.value&0b11011111
	
	@property
	def NT(self):
		return (self.value&0b01000000>0)
	@NT.setter 
	def NT(self, value):
		if (value):
			self.value = self.value|0b01000000
		else:
			self.value = self.value&0b10111111
	
	@property
	def IV(self):
		return (self&0b10000000>0)	
	@IV.setter 
	def IV(self, value):
		if (value):
			self = self|0b10000000
		else:
			self = self&0b01111111

class QDS(QUALITY):
	"""docstring for QDS"""
	@property
	def OV(self):
		return (self.value&0b00000001>0)
	@OV.setter 
	def OV(self, value):
		if (value):
			self.value = self.value|0b00000001
		else:
			self.value = self.value&0b11111110

class SIQ(QUALITY):
	@property
	def byte(self):
		return self.value&0b11111110

	@property
	def SPI(self):
		return (self.value&0b00000001>0)
	@SPI.setter 
	def SPI(self, value):
		if (value):
			self.value = self.value|0b00000001
		else:
			self.value = self.value&0b11111110

class DIQ(QUALITY):
	@property
	def byte(self):
		return self.value&0b11111100

	@property
	def DPI(self):
		return (self.value&0b00000011)
	@DPI.setter 
	def DPI(self, value):
		if (value):
			self.value = (self.value&0b11111100)|(value&3)

class IOA(bytearray):
	def __init__(self, value):
		super(IOA, self).__init__(value)
	@property
	def addr(self):
		if (IOA_LEN==2):
			return (self[0]|(self[1]<<8))
		else:
			return (self[0]|(self[1]<<8)|(self[2]<<16))
	
	@addr.setter 
	def addr(self, value):
		self[0] = value&0xFF
		self[1] = (value>>8)&0xFF
		if (IOA_LEN!=2):
			self[2] = (value>>16)&0xFF

class M_SP_NA_1(IOA): # 1
	TypeId = 1
	def __init__(self, value):
		super(M_SP_NA_1, self).__init__(value)

	@property
	def value(self):
		return SQI(self[IOA_LEN]).SPI

	@property
	def quality(self):
		return SQI(self[IOA_LEN]).byte

	@property
	def siq(self):
		return SQI(self[IOA_LEN])

class M_DP_NA_1(IOA): # 3
	TypeId = 3
	def __init__(self, value):
		super(M_DP_NA_1, self).__init__(value)

	@property
	def value(self):
		return DIQ(self[IOA_LEN]).DPI
	@property
	def quality(self):
		return SQI(self[IOA_LEN]).byte
	@property
	def diq(self):
		return DIQ(self[IOA_LEN])

class M_SP_TB_1(M_SP_NA_1): # 30
	TypeId = 30
	def __init__(self, value):
		super(M_SP_TB_1, self).__init__(value)

	@property
	def time(self):
		return cp56time2a_to_time(self[IOA_LEN+1:IOA_LEN+9])

class M_DP_TB_1(M_DP_NA_1): # 31
	TypeId = 31
	def __init__(self, value):
		super(M_DP_TB_1, self).__init__(value)

	@property
	def time(self):
		return cp56time2a_to_time(self[IOA_LEN+1:IOA_LEN+9])

class M_ME_NC_1(IOA): # 13
	TypeId = 13
	def __init__(self, value):
		super(M_ME_NC_1, self).__init__(value)
	
	def __str__(self):
		return f'IOA: {self.addr} Value: {self.value}'
	@property
	def quality(self):
		return QDS(self[IOA_LEN+4]).byte

	@property
	def value(self):
		return unpack("<f",self[IOA_LEN:IOA_LEN+4])[0]

	@property
	def qds(self):
		return QDS(self[IOA_LEN+4])

class M_ME_TF_1(M_ME_NC_1): # 36
	TypeId = 36
	def __init__(self, value):
		super(M_ME_TF_1, self).__init__(value)
	
	def __str__(self):
		return f'IOA: {self.addr} Value: {self.value}, Time: {self.time}'

	@property
	def time(self):
		return cp56time2a_to_time(self[IOA_LEN+5:IOA_LEN+13])

class C_CS_NA_1(IOA): # 103
	TypeId = 103
	def __init__(self, value):
		super(M_SP_TB_1, self).__init__(value)

	@property
	def time(self):
		return cp56time2a_to_time(self[IOA_LEN:IOA_LEN+8])