import logging
START = 0x68

ASDU_LEN 	= 2
IOA_LEN  	= 3
COT_LEN		= 2

COT_TYPES = {
	1:"COT_PERIODIC",
	2:"COT_BACKGROUND",
	3:"COT_SPONTANEOUS",
	4:"COT_INITIALISED",
	5:"COT_REQUEST",
	6:"COT_ACTIVATION",
	7:"COT_ACTIVATIONCONFIRM",
	8:"COT_DEACTIVATION",
	9:"COT_DEACTIVATIONCONFIRM",
	10:"COT_ACTIVATIONTERMINATION",
	11:"COT_REMOTECOMMAND",
	12:"COT_LOCALCOMMAND",
	13:"COT_FILETRANSFER",
	20:"COT_INTERROGATION"
}

U_FRAME = {
	"STARDT_ACT":b'\x07\x00\x00\x00',
	"STARDT_CON":b'\x0B\x00\x00\x00',
	"TESTFR_ACT":'\x43\x00\x00\x00',
	"TESTFR_CON":'\x83\x00\x00\x00',
	"STOPDT_ACT":'\x13\x00\x00\x00',
	"STOPDT_CON":'\x23\x00\x00\x00'
}

def log_init():
	log = logging.getLogger('IEC104client')
	log.setLevel(logging.INFO)
	formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
	#file log
	tofile = logging.FileHandler('IEC104client.log','a')
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