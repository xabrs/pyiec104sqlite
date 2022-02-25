from iec104.define import *
from iec104.ioa import *
import logging

log = logging.getLogger('IEC104client')

IOA_TYPES = {
	1:(M_SP_NA_1,1),		# Single-point information
	3:(M_DP_NA_1,1),		# Double-point information
	# 5:"M_ST_NA_1",		# Step position information
	# 7:"M_BO_NA_1",		# Bitstring of 32 bit
	# 9:"M_ME_NA_1",		# Measured value, normalized value
	13:(M_ME_NC_1,5),		# Measured value, short floating point value		
	30:(M_SP_TB_1,8),		# Single-point information with time tag CP56Time2a
	31:(M_DP_TB_1,8),		# Double-point information with time tag CP56Time2a
	# 32:"M_ST_TB_1",		# Step position information with time tag CP56Time2a
	# 34:"M_ME_TD_1",		# Measured value, normalized value with time tag CP56Time2a
	36:(M_ME_TF_1,12),		# Measured value, short floating point value with time tag CP56Time2a
	# 37:"M_IT_TB_1",		# Integrated totals value with time tag CP56Time2a
	# 45:"C_SC_NA_1",		# Single command
	# 46:"C_DC_NA_1",		# Double command
	# 47:"C_RC_NA_1",		# Regulating step command
	# 48:"C_SE_NA_1",		# Set point command, normalised value
	# 51:"C_BO_NA_1",		# Bitstring of 32 bit
	# 58:"C_SC_TA_1",		# Single command with time tag CP56Time2a
	# 59:"C_DC_TA_1",		# Double command with time tag CP56Time2a
	# 70:"M_EI_NA_1",		# End of initialization
	# 100:"C_IC_NA_1",		# Interrrogation command
	# 101:"C_CI_NA_1",		# Counter interrrogation command
	103:(C_CS_NA_1,7),		# Clock syncronization command
	# 104:"C_TS_NB_1",		# Test command
	# 105:"C_RP_NC_1"		# Reset process command
}

class asdu(object):
	TypeId = 0
	NumIx = 0
	CauseTx = 0
	Negative = 0
	Test = 0
	OA = 0
	Addr = 0
	ioa = []

	def __init__(self,data=bytearray(0)):
		if (len(data)>0):
			self.parse(data)

	def parse(self,data):
		i = 0
		self.TypeId = data[0]
		self.NumIx = data[1]&0x7F
		self.CauseTx = data[2]&0x3F
		self.Negative = data[2]>>6&1
		self.Test = data[2]>>7&1
		self.OA = data[3]
		self.Addr = data[4]
		i = 5
		if (ASDU_LEN==2):
			self.Addr = self.Addr|data[5]<<8
			i = 6
		if (IOA_TYPES.get(self.TypeId)==None):
			log.error(f'IOA TYPE {self.TypeId} not defined')
			return
		self.ioa = []
		for x in range(self.NumIx):
			try:
				ioa_class, ioa_bytes = IOA_TYPES.get(self.TypeId)
				self.ioa.append(ioa_class(data[i:i+IOA_LEN+ioa_bytes]))
			except Exception as e:
				log.error(e)
			finally:
				i += IOA_LEN+ioa_bytes

	def dump(self):
		log.info(f'ASDU: TypeId: {self.TypeId}, NumIx: {self.NumIx}, CauseTx: {self.CauseTx}={COT_TYPES[self.CauseTx]}, Addr: {self.Addr}')
		for x in self.ioa:
			log.info(f'{x}')
