This folder contains all the code necessary to find, identify and decode bluetooth advertising packages.

For plotting where necessary try and use the plot helpers. 

YOU SHOULD ONLY CHANGE CODE WITHIN THE BLE.py FILE. THE SECTIONS THAT YOU NEED TO CHANGE ARE BETWEEN BLOCKS LIKE THIS:

#############################################################
    #############################################################
    #############################################################
    #############################################################
    
    CHANGE STUFF IN BETWEEN HERE
    
    #############################################################
    #############################################################
    #############################################################
    #############################################################
    
    
Here's what every file does:

#-----------BLEMain.py-------------------------------------------------------

Main script to capture and process BLE advertising packets.

- Configures the Radio
- Captures I/Q Data
- Decodes BLE packets using methods defined in BLE.py
- Outputs decoded packet information


#-----------------Hardware_Abstraction_Layer.py-------------------------------------------------

Manages SDR interaction with your computer

- It can be used with more than just a pluto but 
- Creates the buffers
- Stops the radio


#--------------------BLE.py----------------------------------------------

Decodes Bluetooth Advertising Packets

- Process I/Q data and process them into binary data streams
- Decodes advertising packets with dynamic whitening and CRC checking
- Outputs decoded packet information


#---------------------BLE_Code_Lookup.py---------------------------------------------

Maps BLE PDU and GAP codes to their respective descriptions


#----------------------plot_helpers.py------------------------

Visualizes I/Q Data and frequency spectrums 
