import numpy as np
import plot_helpers as ph
import BLE_Code_Lookup as lookup
# BLE Methods ----------------------------------------------------------------------------

#-----------------------------------------------------------------------------------------


#This code is meant to teach students the basics of Bluetooth Low Energy decoding using the Pluto SDR

# Code created by: Galahad Wernsing
# Modified for ECE 331X by: Samuel Forero
# 11/25/2024

#-----------------------------------------------------------------------------------------

def get_bit_stream(data_stream, downsample_ratio = 2):
	# Don't change the Downsample ratio
	
	
	#############################################################
    #############################################################
    #############################################################
    #############################################################
	
	# Step 1: Extract the phase of the signal and make it continous
	
	
	 # Step 2: Downsample the phase data to reduce complexity
	downsampled_phase = continuous_phase[::downsample_ratio]
	
	
	
    # Step 3: Compute the phase difference (frequency changes)
	
	
	# Step 4: Plot the phase differential
	
	
	#############################################################
    #############################################################
    #############################################################
    #############################################################
    
	return np.greater(freq_data, 0)


#-----------------------------------------------------------------------------------------

def dewhiten(bits, channel=38): 
	return whiten_dynamic(bits, channel)


#-----------------------------------------------------------------------------------------

def whiten(bits, channel=38): 
	return whiten_dynamic(bits, channel)


#-----------------------------------------------------------------------------------------

def whiten_dynamic(bits, channel=38):
	# This part of the code should be done using an LFSR Loop
	
	# setup polynomial
	polynomial = 8*[0]
	
	#############################################################
    #############################################################
    #############################################################
    #############################################################
	exponents = [] # from core spec
	#############################################################
    #############################################################
    #############################################################
    #############################################################
    
    
	
	for x in exponents: polynomial[x] = 1
	working_poly = np.array(polynomial[:-1])
	
	# setup registers
	channel_array = [int(x) for x in format(channel, "0>6b")]
	state = np.array([1] + channel_array, dtype=int) # from core spec
	out_array = np.array([], dtype=int)
	
	# LFSR loop
	for x in range(len(bits)):
	
	#############################################################
    #############################################################
    #############################################################
    #############################################################
		# add bit to the output array
		
	#############################################################
    #############################################################
    #############################################################
    #############################################################
		
		
		# add a 0 to the front of the state array
		# this will be changed to a 1 if needed by the xor
		state = np.insert(state[:-1], 0, 0)
		
		# feedback is done as a single xor step
		xor_array = out_bit*working_poly
		state = np.bitwise_xor(state, xor_array)
		
		
	return np.bitwise_xor(bits, out_array)


#-----------------------------------------------------------------------------------------

def get_CRC(bits):
	# my numpy array implementation was 10x slower, I don't know why
	# this may be easier to read than the whitening, input data is handled differently
	
	exponents = [0,1,3,4,6,9,10] # from core spec, final tap is taken care of with new bit
	
	# setup registers
	state = 6*[1,0,1,0] # from core spec
	
	for bit in bits:
		new_bit = state[-1] ^ bit
		state = [0] + state[:-1]
		if new_bit == 0: continue
		for gate in exponents:
			state[gate] = state[gate]^1
		
	return state[::-1]


#-----------------------------------------------------------------------------------------

def check_CRC(bits, crc):
	a = get_CRC(bits)
	return np.array_equal(a, crc)


#-----------------------------------------------------------------------------------------

def flip_chunk_bytes(chunk_data):
	out = np.zeros(1, dtype=int)
	for i in range(len(chunk_data)//8):
		b = chunk_data[8*i:8*i+8]
		out = np.concatenate((out, b[::-1]))
	out = out[1:]
	return out


#-----------------------------------------------------------------------------------------

def hexme(data):
	return hex(intme(data))


#-----------------------------------------------------------------------------------------

def intme(data):
	return int("0" + "".join([str(x) for x in data]),2)


#-----------------------------------------------------------------------------------------

def channel_printer(packets_dictionary, offset_time = 0):
	sort_keys = sorted(packets_dictionary.keys())
	for key in sort_keys: # keys are timestamps, which are at symbol rate
		time = round((key/1e3) + offset_time,3)
		ad_packet_printer(packets_dictionary[key], time)


#-----------------------------------------------------------------------------------------

def ad_packet_printer(decoded_packet, time):
	if decoded_packet == []: return # covers for short packet fail
	
	print("Found an advertising packet from %s on channel %s at time %sms!" % (decoded_packet["Advertising Address"], decoded_packet["channel"], time))
	
	print("PDU type: %s" % lookup.PDU_Lookup(decoded_packet["PDU"]))
	
	print("Length: %s bytes" % decoded_packet["Length"])
	
	if len(decoded_packet["PDU Chunks"]) > 0:
		print("Payload Chunks:")
		
		for i in range(len(decoded_packet["PDU Chunks"])):
			print("	Chunk %s:" % i)
			print("		Length: %s bytes" % decoded_packet["PDU Chunks"][i]["length"])
			print("		Gap Code: %s" % lookup.GAP_Lookup(decoded_packet["PDU Chunks"][i]["GAP Code"]))
			print("		Data: %s" % hexme(decoded_packet["PDU Chunks"][i]["data"]))
		
	else: print("No Payload Chunks")
	
	print("And the CRC %sed!" % decoded_packet["CRC"])
	print(80*"-")


#-----------------------------------------------------------------------------------------

def decode_ad_packet(packet_bits, channel=38):
	if len(packet_bits) < 300: return [] # not amazing but it doesn't crash
	
	sections = {}
	unwhite = dewhiten(packet_bits, channel) # over dewhiten so I only have to call it once
	
	header = unwhite[:16]
	
	sections["PDU"] = intme(header[:4][::-1]) # int here and gap code to make lookup table easier, not printing the value directly
	
	length = intme(header[8:14][::-1])
	
	sections["Length"] = length
	
	PDU_length_bits = length*8
	
	PDU = unwhite[16:16+PDU_length_bits]
	AA = PDU[:6*8][::-1]
	sections["Advertising Address"] = hexme(AA)
	
	offset = 6*8
	
	PDU_Chunks = []
	for x in range(37): # I know this is the maximum I think
		if offset >= PDU_length_bits: break
		
		chunk = {}
		chunk_length = intme(PDU[offset:offset+8][::-1])
		chunk["length"] = chunk_length
		
		chunk["GAP Code"] = intme(PDU[offset+8:offset+16][::-1])
		
		new_offset = offset + 8*(chunk_length+1)
		
		chunk_data = flip_chunk_bytes(PDU[offset+16:new_offset])
		chunk["data"] = "".join([str(x) for x in chunk_data])
		
		PDU_Chunks = PDU_Chunks + [chunk]
		
		offset = new_offset
		
	sections["PDU Chunks"] = PDU_Chunks
	
	crc_off = offset+16
	crclen = 24
	CRC = unwhite[crc_off:crc_off+crclen]
	
	crc_pass = check_CRC(unwhite[:crc_off], CRC)
	
	sections["CRC"] = crc_pass
	sections["channel"] = channel
	if crc_pass == "fail":
		#print("failed crc channel %s" % channel)
		pass
		#return [] # I can do a fail check in the printing function
	return sections


#-----------------------------------------------------------------------------------------

def fix_CRC(packet_bits, CRC):
	test = packet_bits
	for i in range(len(packet_bits)):
		test[i] = test[i]^1
		if get_CRC_alt(test) == CRC: return test
		test = packet_bits
	return []


#-----------------------------------------------------------------------------------------

def decode_ad_channel(data, dwnsmpl = 2, chan_num = 38):
	
	bits = get_bit_stream(data, downsample_ratio = dwnsmpl)

	packet_start_locations = find_advertising_packets(bits)

	packets = []
	for loc in packet_start_locations:
		AA_start = loc+40
		packet = bits[AA_start:AA_start+300*8] # packet must be shorter than this, at least for pre-5.0 packets
		packets = packets + [packet]

	processed_packets = process_ad_packet_chunks(packets, chan_num)
	
	return {time:data for time, data in zip(packet_start_locations, processed_packets)}


#-----------------------------------------------------------------------------------------

def process_ad_packet_chunks(chunks, channel):
	if channel not in [37,38,39]: return 0
	found_packets = []
	for chunk in chunks:
		out = decode_ad_packet(chunk, channel)
		found_packets = found_packets + [out]
	
	return found_packets




#-----------------------------------------------------------------------------------------

preamble_and_aa = np.array([0,1,0,1,0,1,0,1,0,1,1,0,1,0,1,1,0,1,1,1,1,1,0,1,1,0,0,1,0,0,0,1,0,1,1,1,0,0,0,1],dtype=bool)
# declaring it outside the methods saves cycle time at the expense of import speed and initial ram overhead

# assuming the preamble and aa don't end the data stream, and if they do you don't have the whole packet anyway
def find_advertising_packets(data_stream):
	return find_bit_pattern(data_stream, preamble_and_aa)


#-----------------------------------------------------------------------------------------

# inputs must be castable to bools
def find_bit_pattern(data_stream, pattern):
	# modified version of algorithm presented here: https://www.reddit.com/r/learnpython/comments/2xqlwj/comment/cp3kgio/

	# May not need explicit cast here
	check_array = data_stream.astype(bool)
	ref_array = pattern.astype(bool)
	
	out_len = len(check_array) - len(ref_array)
	
	out_array = np.ones(out_len).astype(bool)
	
	for i in range(len(ref_array)):
		if ref_array[i]:
			out_array *=  check_array[i:i+out_len]
		else:
			out_array *= ~check_array[i:i+out_len]
	
	
	return (np.nonzero(out_array)[0])
