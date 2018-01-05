# settings apply only to the device tier

# adc sample rate per second
samplerate = 5000

# uart speed
baudrate = 115200

# set to True if raspberry pi is in use
raspberrypi = True

# com port
port = '/dev/ttyAMA0'	# for raspberry pi
# port = 'COM39'		# for windows

# single measurement mode if set to False
runcontinuosly = True

# time between measurements
sleeptime = 30

# if set to True raw data is processed
analyse = False

# if set to True plots are saved as png files in data catalog
plot = True

# relative or absolute path to a catalog with measurement files
datacatalog = 'data/'

# if set to True data is read from a file
demo = False

# file with data used in demo mode
sampledatafile = '20170910_151226_646_time_sample_data.txt'

# switch on/off flag for ppm measurement
ppm_on = True

# switch on/off flag for temperature measurement
t_on = False

# if set to True data is uploaded to a server tier
upload_to_server = True

# POST endpoint
data_server = 'http://localhost:3000/ppms'