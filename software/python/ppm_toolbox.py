import numpy as np
import math
import serial
import base64
import array
import datetime
import ntpath
from scipy.optimize import curve_fit
from scipy.signal import butter, filtfilt
import matplotlib.pyplot as plt
import os
import collections


def sine_damp(x, x0, f, t0, A, y0):
	"""Sine function whose amplitude for positive t0 approaches y0 as x (time in the context of ppm) increases

	Args:
		x (array of floats 64): independent variable, time in the context of ppm
		x0 (float64): sine phase shift
		f (float64): frequency
		t0 (float64): decay rate
		A (float64): amplitude
		y0 (float64): offset
	Returns:
		array of floats 64
	"""

	return y0 + damp(x, t0, A) * np.sin(2 * math.pi * (x - x0) * f)


def damp(x, t0, A):
	"""e to the power of -x/t0

	Args:
		x (array of floats 64): independent variable, time in the context of ppm
		t0 (float64): decay rate
		A (float64): amplitude
	Returns:
		array of floats 64
	"""
	return A * np.exp(-x / t0)


def analyze_ppm(voltagesamples, samplerate, freqrange=[2125.0, 2135.0], fitrangepct=[0.0, 100.0]):
	"""This function tries to find position of a ppm peak in the raw signal. The following steps are made:
	1. DFT calculation
	2. looking for a frequency with max amplitude in the specified range of the DFT
	3. applying the Butterworth filter in the 10 Hz range centered around frequency found in step 2
	4. fitting filtered signal to the damped sine model

	Args:
		voltagesamples (list of ints): voltage samples in mV
		samplerate (int): adc sample rate per second
		freqrange (array of floats): ppm peak search range specified in Hz
		fitrangepct (array of floats): fit range specified in %
	Returns:
		named tuple with the following fields:
			B (float64): Earth's magnetic field strength
			xfft (array of floats 64): dft sample frequencies
			yfft (array of floats 64): dft values
			filtered (array of floats 64): voltage samples in the time domain after applying the Butterworth filter
			frezfit (float64): resonance frequency calculated by fitting to the model
			frezfft (float64): resonance frequency calculated from dft
			frezfft_amplitude (float64): ppm peak amplitude in the frequency domain
			t0 (float64): signal decay time constant in seconds
			A (float64): amplitude parameter from damp function
			x0_error (float64): standard deviation error of the sine phase shift
			f_error (float64): standard deviation error of the frequency
			t0_error (float64): standard deviation errorof the signal decay time constant
			A_error (float64): standard deviation error of the amplitude
			y0_error (float64): standard deviation error of the offset
	"""

	# calculate dft
	avg = sum(voltagesamples) / len(voltagesamples)
	filtered = [x - avg for x in voltagesamples]
	N = filtered.__len__()
	xfft = np.fft.rfftfreq(N, d=1 / samplerate)
	yfft = np.fft.rfft(filtered)

	# calculate frequency with max amplitude in the range specified by freqrange
	rangefrom = [i for i, v in enumerate(xfft) if v >= freqrange[0]]
	rangeto = [i for i, v in enumerate(xfft) if v <= freqrange[1]]
	subxfft = xfft[rangefrom[0]:rangeto[-1] + 1]
	subyfft = yfft[rangefrom[0]:rangeto[-1] + 1]
	fftmax_index = np.argmax(np.abs(subyfft))
	fftrez = subxfft[fftmax_index]
	fftrez_amplitude = np.abs(subyfft)[fftmax_index]

	filtered = butter_bandpass_filter(filtered, fftrez - 5, fftrez + 5, samplerate, order=3)

	t = np.linspace(0, N / samplerate, num=N)

	fit_results = curve_fit(sine_damp, t[int(fitrangepct[0] * N / 100):int(fitrangepct[1] * N / 100)],
							filtered[int(fitrangepct[0] * N / 100):int(fitrangepct[1] * N / 100)],
							p0=[0, fftrez, 2.0, 400.0, 0.0])
	x0 = fit_results[0][0]
	f = fit_results[0][1]
	t0 = fit_results[0][2]
	A = fit_results[0][3]
	y0 = fit_results[0][4]
	# compute standard deviation errors
	total_error = np.sqrt(np.diag(fit_results[1]))
	x0_error = total_error[0]
	f_error = total_error[1]
	t0_error = total_error[2]
	A_error = total_error[3]
	y0_error = total_error[4]

	ppmresults = collections.namedtuple('ppmresults',
										['B', 'xfft', 'yfft', 'filtered',
										'frezfit', 'frezfft', 'frezfft_amplitude',
										 't0', 'A', 'x0_error', 'f_error',
										 't0_error', 'A_error', 'y0_error'])

	return ppmresults(23.496241 * f, xfft, np.abs(yfft), filtered, f, fftrez, fftrez_amplitude, t0, np.abs(A),
				x0_error, f_error, t0_error, A_error, y0_error)


def read_temperature_from_device_uart(baudrate, port):
	"""This function triggers temperature measurement then returns result. Data transmission channel is uart.

	Args:
		baudrate (int): uart transmission speed
		port (str): uart port
	Returns:
		named tuple with the following fields:
			t (todo): temperature in degrees celsius
			takenAt (todo): unix timestamp
	"""

	# open serial port
	serialport = serial.Serial(timeout=2)
	serialport.baudrate = baudrate
	serialport.port = port
	serialport.open()

	# start T procedure
	serialport.timeout = None
	serialport.write(b'T')
	print(str(datetime.datetime.utcnow())[:-3] + ': Start T command sent')
	takenAt = (datetime.datetime.utcnow() - datetime.datetime(1970, 1, 1)) / datetime.timedelta(seconds=1)

	# wait for result
	singleCharacter = serialport.read()
	valuesstr = ''
	valuesstr += singleCharacter.decode(encoding='utf-8')
	serialport.timeout = 1
	while singleCharacter.__len__() > 0:
		singleCharacter = serialport.read()
		if singleCharacter.__len__() > 0:
			valuesstr += singleCharacter.decode(encoding='utf-8')
	serialport.close()
	temperature = collections.namedtuple('temperature', ['t', 'takenAt'])
	return temperature(float(valuesstr)/16.0, takenAt)
	
				
def read_ppm_from_device_uart(baudrate, port, samplerate):
	"""This function triggers ppm measurement then records and returns voltage samples. Data transmission channel is uart.

	Args:
		baudrate (int): uart transmission speed
		port (str): uart port
		samplerate (int): adc sample rate per second
	Returns:
		named tuple with the following fields:
			voltagesamples (list of ints): voltage samples in mV
			starttime (float): unix timestamp representing time when first voltage sample were taken
			samplerate (int): adc sample rate per second
			base64samples (str): voltage samples encoded to base64
	"""

	# open serial port
	serialport = serial.Serial(timeout=2)
	serialport.baudrate = baudrate
	serialport.port = port
	serialport.open()

	# start ppm procedure
	serialport.timeout = None
	serialport.write(b'S')
	print(str(datetime.datetime.utcnow())[:-3] + ': Start PPM command sent')

	# wait for adc results
	singleCharacter = serialport.read()
	transmissionstart = datetime.datetime.utcnow()
	print(str(transmissionstart)[:-3] + ': Data download started')
	valuesstr = ''
	valuesstr += singleCharacter.decode(encoding='utf-8')
	serialport.timeout = 1
	while singleCharacter.__len__() > 0:
		singleCharacter = serialport.read()
		if singleCharacter.__len__() > 0:
			valuesstr += singleCharacter.decode(encoding='utf-8')

	transmissionend = datetime.datetime.utcnow()
	print(str(transmissionend)[:-3] + ': Data download time: ' + str(
		transmissionend - transmissionstart + datetime.timedelta(seconds=-1)))
	serialport.close()

	# decode results from base64
	return decode_from_base64(valuesstr, samplerate, adcstoptime = transmissionstart)

def decode_from_base64(base64samples, samplerate, adcstarttime = None, adcstoptime = None):
	"""Decode 12-bit voltage samples encoded in base64
	Args:
	    base64samples (str): voltage samples encoded to base64
	    samplerate (int): adc sample rate per second
	    adcstarttime (datetime): start time of adc sampling (either adcstarttime or adcstoptime must not be None)
	    adcstoptime (datetime): stop time of adc sampling

	Returns:
		named tuple with the following fields:
			voltagesamples (list of ints): voltage samples in mV
			starttime (float): unix timestamp representing time when first voltage sample were taken
			samplerate (int): adc sample rate per second
			base64samples (str): voltage samples encoded to base64
	"""

	# decode results from base64
	decoded = base64.b64decode(base64samples)
	decodedbytes = array.array('B', decoded)

	voltagesamples = []
	for z in range(2, decodedbytes.__len__(), 3):
		adc1 = ((decodedbytes[z - 2] << 4) & 0xFF0) + ((decodedbytes[z - 1] >> 4) & 0x00F)
		voltagesamples.append(adc1)
		adc2 = ((decodedbytes[z - 1] << 8) & 0xF00) + (decodedbytes[z] & 0xFF)
		voltagesamples.append(adc2)

	if adcstarttime is None:
		adcstarttime = adcstoptime + datetime.timedelta(seconds=-voltagesamples.__len__() / samplerate)
	
	timestamp = (adcstarttime - datetime.datetime(1970, 1, 1)) / datetime.timedelta(seconds=1)

	rawdata = collections.namedtuple('rawdata', ['voltagesamples', 'starttime', 'samplerate', 'base64samples'])
	return rawdata(voltagesamples, timestamp, samplerate, base64samples)


def read_ppm_from_file(filename, presenttime = True):
	"""This function reads single measurement data from a file

	Args:
		filename (str): path to a file with voltage samples
		presenttime (bool): if False time is parsed from the filename, otherwise present utc time is taken
	Returns:
		named tuple with the following fields:
			voltagesamples (list of ints): voltage samples in mV
			starttime (float): unix timestamp representing time when first voltage sample were taken
			samplerate (int): adc sample rate per second
			base64samples (str): voltage samples encoded to base64
	"""
	if not presenttime:
		measurementtime = datetime.datetime.strptime(ntpath.basename(filename)[:19], '%Y%m%d_%H%M%S_%f')
	else:
		measurementtime = datetime.datetime.utcnow()
	with open(filename) as f:
		content = f.readlines()

	adctab = []

	samplerate = 1 / (float(content[1].split()[0]) - float(content[0].split()[0]))

	for line in content:
		splitted = line.split()
		adctab.append(int(splitted[1]))

	# encode to base64 as in the microcontroller
	adctab_bytesplitted = []
	i = 0
	# take two 12 bit values and split them into 3 bytes
	for adc in adctab:
		if i % 2 == 0:
			adc1 = adc
		else:
			adc2 = adc
			adctab_bytesplitted.append(adc1 >> 4);
			adctab_bytesplitted.append(((adc1 & 0xF) << 4) | ((adc2 >> 8) & 0xF));
			adctab_bytesplitted.append(adc2 & 0xFF);
		i += 1
	# encode to base64
	base64encoded = base64.b64encode(bytearray(adctab_bytesplitted)).decode("utf-8")

	rawdata = collections.namedtuple('rawdata', ['voltagesamples', 'starttime', 'samplerate', 'base64samples'])
	timestamp = (measurementtime - datetime.datetime(1970, 1, 1)) / datetime.timedelta(seconds=1)
	return rawdata(adctab, timestamp, samplerate, base64encoded)


def butter_bandpass(lowcut, highcut, samplerate, order=5):
	"""This function wrapes scipy.signal.butter function
	For details visit http://scipy-cookbook.readthedocs.io/items/ButterworthBandpass.html
	and https://docs.scipy.org/doc/scipy-0.14.0/reference/generated/scipy.signal.butter.html

	Args:
		lowcut (float64): low cut frequency in Hz
		highcut (float64): high cut frequency in Hz
		samplerate (int): adc sample rate per second
		order (int): order of the Butterworth filter
	Returns:
		numerator (b) and denominator (a) polynomials of the filter
	"""
	nyq = 0.5 * samplerate
	low = lowcut / nyq
	high = highcut / nyq
	b, a = butter(order, [low, high], btype='band')
	return b, a


def butter_bandpass_filter(data, lowcut, highcut, samplerate, order=5):
	"""Applies the Butterworth filter and returns results
	For details visit http://scipy-cookbook.readthedocs.io/items/ButterworthBandpass.html

	Args:
		data (list of floats): data to be filtered
		lowcut (float64): low cut frequency in Hz
		highcut (float64): high cut frequency in Hz
		samplerate (int): adc sample rate per second
		order (int): order of the Butterworth filter
	Returns:
		filtered data as array of floats 64
	"""

	# get numerator (b) and denominator (a) polynomials
	b, a = butter_bandpass(lowcut, highcut, samplerate, order=order)
	# apply the filter
	y = filtfilt(b, a, data)
	return y


def plot_results(rawdata, retv, catalog, show=True):
	"""This function plots ppm results. First figure contains the following plots: raw signal in the time domain,
	signal in the frequency domain, signal in the time domain after applying the Butterworth filter.
	Second figure presents zoom at ppm peak in the frequency domain.

	Args:
		rawdata: named tuple returned from the read_from_device_uart function
		retv: named tuple returned from the analyze_ppm function
		catalog (str): path to the location where plots are saved
		show (bool): if True plots are displayed
	"""

	N = rawdata.voltagesamples.__len__()
	t = np.linspace(0, N / rawdata.samplerate, num=N)
	mtime = datetime.datetime.utcfromtimestamp(rawdata.starttime).strftime("%Y-%m-%d %H:%M:%S")
	timestr = datetime.datetime.utcfromtimestamp(rawdata.starttime).strftime("%Y%m%d_%H%M%S_%f")[:-3]

	fig1 = plt.figure(1, figsize=(7, 10))

	plt.subplot(311)
	plt.plot(t, [x / 1000.0 for x in rawdata.voltagesamples])
	plt.grid()
	plt.xlabel('Time [s]')
	plt.ylabel('Voltage [V]')
	plt.title('Signal in the time and the frequency domain\n' + mtime + ' UTC')

	ax = plt.subplot(312)
	plt.plot(retv.xfft, retv.yfft)
	plt.grid()
	plt.xlabel('Frequency [Hz]')
	plt.ylabel('Amplitude [a.u.]')
	plt.xlim([1800, 2500])
	plt.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))
	plt.subplots_adjust(hspace=0.35)
	os.makedirs(catalog, exist_ok=True)

	ydamp = damp(t, retv.t0, retv.A)

	plt.subplot(313)
	plt.plot(t, [x / 1000.0 for x in retv.filtered], label='PPM signal')
	plt.plot(t, [x / 1000.0 for x in ydamp], 'r--', linewidth=2.0, label='signal damping')
	plt.plot(t, [x / -1000.0 for x in ydamp], 'r--', linewidth=2.0)
	plt.grid()
	plt.title('Filtered signal')
	plt.xlabel('Time [s]')
	plt.ylabel('Voltage [V]')
	plt.legend()
	plt.savefig(catalog + '/' + timestr + '_1.png', bbox_inches='tight')

	fig2 = plt.figure(2)
	plt.plot(retv.xfft, retv.yfft, label='measured signal in\nthe frequency domain')
	plt.grid()
	plt.xlabel('Frequency [Hz]')
	plt.ylabel('Amplitude [a.u.]')
	plt.title('PPM signal in the frequency domain\n' + mtime + ' UTC')
	plt.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))
	plt.xlim([2100, 2150])
	plt.vlines(retv.frezfit, 0, retv.frezfft_amplitude * 1.1, linestyles='--', label='resonance frequency\nfrom fit')
	plt.legend(loc=2)
	plt.savefig(catalog + '/' + timestr + '_2.png', bbox_inches='tight')

	if show:
		plt.show()
	fig1.clear()
	fig2.clear()
	plt.close()


def save_raw_data(catalog, raw_data):
	"""Save raw data to a file

	Args:
		catalog (str): path to a file storage
		raw_data: named tuple returned from the read_from_device_uart function
	Returns:
		filename
	"""

	os.makedirs(catalog, exist_ok=True)
	filename = datetime.datetime.utcfromtimestamp(raw_data.starttime).strftime("%Y%m%d_%H%M%S_%f")[:-3] + "_time.txt"
	measurement_file = open(os.path.join(catalog, filename), 'w')
	for (i, adc) in enumerate(raw_data.voltagesamples):
		measurement_file.write(str(i / raw_data.samplerate) + '\t' + str(adc) + '\n')
	measurement_file.close()

	return filename


def save_raw_data_FFT(catalog, results, starttime):
	"""Save raw data in the frequency domain to a file

	Args:
		catalog (str): path to a file storage
		results: named tuple returned from the analyze_ppm function
		starttime (float): unix timestamp representing time when first voltage sample were taken
	Returns:
		filename
	"""

	os.makedirs(catalog, exist_ok=True)
	filename = datetime.datetime.utcfromtimestamp(starttime).strftime("%Y%m%d_%H%M%S_%f")[:-3] + "_frequency.txt"
	measurement_file = open(os.path.join(catalog, filename), 'w')
	for (i, adc) in enumerate(results.yfft):
		measurement_file.write(str(results.xfft[i]) + '\t' + str(adc) + '\n')
	measurement_file.close()

	return filename


def save_results(catalog, raw_data, results):
	"""Save analysis results to a file

	Args:
		catalog (str): path to a file storage
		raw_data: named tuple returned from the read_from_device_uart function
		results: named tuple returned from the analyze_ppm function
	"""

	analysis_results_file_path = os.path.join(catalog, datetime.datetime.utcfromtimestamp(raw_data.starttime).strftime("%Y%m%d") + ".txt")
	analysis_results_file = open(analysis_results_file_path, 'a+')

	# write header
	if os.stat(analysis_results_file_path).st_size == 0:
		analysis_results_file.write('UTC' +
								'\tB' +
								'\tfit resonance frequency' +
								'\tfft resonance frequency' +
								'\tt0' +
								'\tfft amplitude' +
								'\tA' +
								'\txc error' +
								'\tw error' +
								'\tt0 error' +
								'\tA error' +
								'\ty0 error' +
								'\n')

	# write results
	analysis_results_file.write(datetime.datetime.utcfromtimestamp(raw_data.starttime).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3] +
							'\t' + "{0:.2f}".format(results.B) +
							'\t' + "{0:.2f}".format(results.frezfit) +
							'\t' + "{0:.2f}".format(results.frezfft) +
							'\t' + "{0:.2f}".format(results.t0) +
							'\t' + "{0:.2f}".format(results.frezfft_amplitude) +
							'\t' + "{0:.2f}".format(results.A) +
							'\t' + "{:.2E}".format(results.x0_error) +
							'\t' + "{:.2E}".format(results.f_error) +
							'\t' + "{:.2E}".format(results.t0_error) +
							'\t' + "{:.2E}".format(results.A_error) +
							'\t' + "{:.2E}".format(results.y0_error) +
							'\n')

	analysis_results_file.close()


class Logger:
	def __init__(self, stream, catalog):
		self.stream = stream
		self.catalog = catalog

	def write(self, data):
		self.stream.write(data)
		self.logfile = open(os.path.join(self.catalog, '_errors.log'), 'a+')
		self.logfile.write(data)
		self.logfile.close()

	def set_catalog(self, catalog):
		self.catalog = catalog
