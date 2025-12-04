# currently supports limes, lime minis, limenet micros (as "lime") and plutos
# "twin lime" is for using the second channel on limes when applicable
# only supports talking to one radio at a time
# there's a soapy binding for plutos but I like the adi library better than soapy. There may be a difference in continuous streaming support but I don't know
# Lime transmit support is currently experimental, it appears to broadcast correctly but only at a low power
# import try blocks are just there to warn you, it'll still allow you to crash your code if you attempt to use them anyway

try:
	import SoapySDR
	from SoapySDR import * # SOAPY_SDR_ constants
except Exception: print("Install soapysdr to use limes")
try:
	import adi
except Exception: print("Install pyadi-iio to use plutos")
import numpy as np

# you don't need to declare them here but it's easier to read
radio_type = ""
sdr = []
# lime specific
buffer = []
rxStream = []
txStream = []

#-----------------------------------------------------------------------------------------

# this will need to be modified if you want to do twin rx on a pluto rev >=c
def make_a_radio(brand, uri="ip:192.168.2.1"):
	if brand not in ["pluto", "lime", "twin lime"]:
		print("invalid radio type")
		return
	
	global radio_type
	radio_type = brand
	
	global sdr
	
	if radio_type == "pluto":
		sdr = adi.Pluto(uri) # use iio_info -s to check the ip address
	
	elif radio_type == "lime":
		sdr = SoapySDR.Device({'driver':'lime'})
	
	elif radio_type == "twin lime":
		sdr = SoapySDR.Device({'driver':'lime'})
	
	else:
		print("whoops - make a radio")
		return


#-----------------------------------------------------------------------------------------

# inputs need to be convertable to integers
def start_receiver(fc, fs, buffsize):
	
	global sdr
	global rxStream # yells on import if you put this inside the if
	
	if radio_type == "pluto":
		sdr.rx_lo = int(fc)
		sdr.sample_rate = int(fs)
		sdr.rx_rf_bandwidth = int(fs)
	
	elif radio_type == "lime":
		# https://discourse.myriadrf.org/t/error-rx-calibration-mcu-error-5-loopback-signal-weak-not-connected-insufficient-gain/7637
		
		start_gain = sdr.getGain(SOAPY_SDR_RX, 0)
		sdr.setGain(SOAPY_SDR_RX, 0, 1024)

		sdr.setAntenna(SOAPY_SDR_RX, 0, 'LNAH')
		sdr.setSampleRate(SOAPY_SDR_RX, 0, fs)
		sdr.setBandwidth(SOAPY_SDR_RX, 0, fs)
		sdr.setFrequency(SOAPY_SDR_RX, 0, fc)


		sdr.setGain(SOAPY_SDR_RX, 0, start_gain)
		
		rxStream = sdr.setupStream(SOAPY_SDR_RX, SOAPY_SDR_CF32, [0])
		sdr.activateStream(rxStream)
	
	elif radio_type == "twin lime":
		
		start_gain_0 = sdr.getGain(SOAPY_SDR_RX, 0)
		start_gain_1 = sdr.getGain(SOAPY_SDR_RX, 1)
		sdr.setGain(SOAPY_SDR_RX, 0, 1024)
		sdr.setGain(SOAPY_SDR_RX, 1, 1024)

		sdr.setAntenna(SOAPY_SDR_RX, 0, 'LNAH')
		sdr.setSampleRate(SOAPY_SDR_RX, 0, fs)
		sdr.setBandwidth(SOAPY_SDR_RX, 0, fs)
		sdr.setFrequency(SOAPY_SDR_RX, 0, fc[0])

		sdr.setAntenna(SOAPY_SDR_RX, 1, 'LNAH')
		sdr.setSampleRate(SOAPY_SDR_RX, 1, fs)
		sdr.setBandwidth(SOAPY_SDR_RX, 1, fs)
		sdr.setFrequency(SOAPY_SDR_RX, 1, fc[1])


		sdr.setGain(SOAPY_SDR_RX, 0, start_gain_0)
		sdr.setGain(SOAPY_SDR_RX, 1, start_gain_1)
		
		rxStream = sdr.setupStream(SOAPY_SDR_RX, SOAPY_SDR_CF32, [0,1])
		sdr.activateStream(rxStream)
	
	else:
		print("whoops - start receiver")
		return
	
	make_a_buffer(buffsize)

#-----------------------------------------------------------------------------------------

# only hand this a power of 2, it makes FFTs efficient later
def make_a_buffer(buff_size):
	global buffer # only need to declare if you're doing assignment
	if radio_type == "pluto":
		sdr.rx_buffer_size = buff_size
	elif radio_type == "lime":
		buffer = np.zeros(buff_size, np.complex64)
	elif radio_type == "twin lime":
		buffer = np.zeros((2,buff_size), np.complex64)
	else:
		print("whoops - make a buffer")
		return


#-----------------------------------------------------------------------------------------

def get_filled_buffer():
	if radio_type == "pluto":
		return sdr.rx()
	elif radio_type == "lime":
		sr = sdr.readStream(rxStream, [buffer], len(buffer))
		return buffer
	elif radio_type == "twin lime":
		sr = sdr.readStream(rxStream, [buffer[0], buffer[1]], np.shape(buffer)[1])
		return buffer
	else:
		print("whoops - get filled buffer")
		return


#-----------------------------------------------------------------------------------------

# doesn't actually turn it off, couldn't come up with a better name
def turn_off_radio():
	if radio_type == "pluto":
		pass # you don't actually need to do anything here
	elif radio_type == "lime" or radio_type == "twin lime":
		if rxStream != []:
			sdr.deactivateStream(rxStream)
			sdr.closeStream(rxStream)
		if txStream != []:
			sdr.deactivateStream(txStream)
			sdr.closeStream(txStream)

	else:
		print("whoops - turn off radio")
		return


#-----------------------------------------------------------------------------------------

def start_transmitter(fc, fs=-1, tx_dbm = -1):
	global sdr
	global txStream
	if radio_type == "pluto":
		sdr.tx_lo = int(fc)
		sdr.tx_hardwaregain_chan0 = tx_dbm
		# does not support separate fs
		# may crash if you call start transmitter before start receiver on a pluto

	elif radio_type == "lime":
		# tx_dbm unused at the moment
		sdr.setGain(SOAPY_SDR_TX, 0, 1024)
		sdr.setAntenna(SOAPY_SDR_TX, 0, 'BAND1')
		sdr.setSampleRate(SOAPY_SDR_TX, 0, fs)
		if fs < 5e6:
			sdr.setBandwidth(SOAPY_SDR_TX, 0, 5e6)
			print("HAL Note: minimum lime tx filter BW 5MHz, lower fs ok")
		else: sdr.setBandwidth(SOAPY_SDR_TX, 0, fs)
		sdr.setFrequency(SOAPY_SDR_TX, 0, fc)
		txStream = sdr.setupStream(SOAPY_SDR_TX, SOAPY_SDR_CF32, [0])
		sdr.activateStream(txStream)
		
	elif radio_type == "twin lime":
		sdr.setGain(SOAPY_SDR_TX, 0, 1024)
		sdr.setGain(SOAPY_SDR_TX, 1, 1024)
		if fs < 5e6:
			sdr.setBandwidth(SOAPY_SDR_TX, 0, 5e6)
			sdr.setBandwidth(SOAPY_SDR_TX, 1, 5e6)
			print("HAL Note: minimum lime tx filter BW 5MHz, lower fs ok")
		else: 
			sdr.setBandwidth(SOAPY_SDR_TX, 0, fs)
			sdr.setBandwidth(SOAPY_SDR_TX, 1, fs)
		sdr.setAntenna(SOAPY_SDR_TX, 0, 'BAND1')
		sdr.setSampleRate(SOAPY_SDR_TX, 0, fs)
		sdr.setFrequency(SOAPY_SDR_TX, 0, fc[0])
		sdr.setAntenna(SOAPY_SDR_TX, 1, 'BAND1')
		sdr.setSampleRate(SOAPY_SDR_TX, 1, fs)
		sdr.setFrequency(SOAPY_SDR_TX, 1, fc[1])
		txStream = sdr.setupStream(SOAPY_SDR_TX, SOAPY_SDR_CF32, [0,1])
		sdr.activateStream(txStream)

	else:
		print("whoops - start transmitter")
		return


#-----------------------------------------------------------------------------------------

# use normalized inputs, ie +-1 is max power
def transmit(iq_samples):
	if radio_type == "pluto":
		return sdr.tx(2**14*iq_samples) # 2**14 used to max out the 16-bit input DAC
		
	elif radio_type == "lime":
		return sdr.writeStream(txStream, [iq_samples], len(iq_samples))
		# I don't know what the lime scaling should be
		# I tested various scales from 1*iq to 2**62*iq, no obvious changes
		# lime tx power appears to be very low
		
	elif radio_type == "twin lime":
		return sdr.writeStream(txStream, [iq_samples[0], iq_samples[1]], len(iq_samples[0]))

	else:
		print("whoops - transmit")
		return
