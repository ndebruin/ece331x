import Hardware_Abstraction_Layer as HAL
import BLE
import plot_helpers as ph
import numpy as np

# Nothing from this code should be changed but it gives hints as to how it works 


# set up the radio -----------------------------------------------------------------------

ad_channels = {37:2402e6, 38:2426e6, 39:2480e6}
channel = 38

fc = 38
fs = 4e6
buff_size = 2**20

print("sample rate: %s" % fs)
print("collection time: %s" % (buff_size/fs))

HAL.make_a_radio("pluto")
HAL.start_receiver(fc, fs, buff_size)

# # read data ------------------------------------------------------------------------------

buffer = HAL.get_filled_buffer()
#buffer = np.fromfile('C:/Users/meflo/Documents/Official Final Master Code/15019-samples.iq', np.complex128)
# process data ---------------------------------------------------------------------------

decoded_channel = BLE.decode_ad_channel(buffer, dwnsmpl=int(fs/1e6), chan_num= 38) 


# print out data -------------------------------------------------------------------------

BLE.channel_printer(decoded_channel)

# turn off the radio ---------------------------------------------------------------------

HAL.turn_off_radio()
