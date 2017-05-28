import ppm_settings as settings

if settings.raspberrypi:
	import matplotlib
	matplotlib.use('Agg')
	
import datetime
import time
import os
import threading

from ppm_toolbox import analyze_ppm
from ppm_toolbox import read_ppm_from_file
from ppm_toolbox import read_ppm_from_device_uart
from ppm_toolbox import read_temperature_from_device_uart
from ppm_toolbox import plot_results


next_call = time.time()

def ppm_measure(runcontinuosly=settings.runcontinuosly, plot=settings.plot):
	try:
		if settings.ppm_on:
			# start measurement
			if settings.demo:
				raw_data = read_ppm_from_file(settings.sampledatafile)
			else:
				raw_data = read_ppm_from_device_uart(settings.baudrate, settings.port, settings.samplerate)

			# analyze
			retv = analyze_ppm(raw_data.voltagesamples, settings.samplerate, fitrangepct=[4.0, 90.0])
			print('B = ' + "{0:.2f}".format(retv.B) + ' nT')
			print('t0 = ' + "{0:.2f}".format(retv.t0) + ' s')
			print('fit resonance frequency = ' + "{0:.2f}".format(retv.frezfit) + ' Hz')
			print('fft resonance frequency = ' + "{0:.2f}".format(retv.frezfft) + ' Hz')

			# save results to a file
			catalog = settings.datacatalog + raw_data.starttime.strftime("%Y%m%d")
			os.makedirs(catalog, exist_ok=True)

			outputFileTimeDomain = open(catalog + '/' + raw_data.starttime.strftime("%Y%m%d_%H%M%S_%f")[:-3] + "_time.txt", 'w')
			for (i, adc) in enumerate(raw_data.voltagesamples):
				outputFileTimeDomain.write(str(i / settings.samplerate) + '\t' + str(adc) + '\n')
			outputFileTimeDomain.close()

			field_output_file = open(catalog + '/' + raw_data.starttime.strftime("%Y%m%d") + ".txt", 'a+')

			# write header
			if os.stat(catalog + '/' + raw_data.starttime.strftime("%Y%m%d") + ".txt").st_size == 0:
				field_output_file.write('UTC' +
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
			field_output_file.write(raw_data.starttime.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3] +
							'\t' + "{0:.2f}".format(retv.B) +
							'\t' + "{0:.2f}".format(retv.frezfit) +
							'\t' + "{0:.2f}".format(retv.frezfft) +
							'\t' + "{0:.2f}".format(retv.t0) +
							'\t' + "{0:.2f}".format(retv.frezfft_amplitude) +
							'\t' + "{0:.2f}".format(retv.A) +
							'\t' + "{:.2E}".format(retv.x0_error) +
							'\t' + "{:.2E}".format(retv.f_error) +
							'\t' + "{:.2E}".format(retv.t0_error) +
							'\t' + "{:.2E}".format(retv.A_error) +
							'\t' + "{:.2E}".format(retv.y0_error) +
							'\n')

			# plot results
			if plot:
				plot_results(raw_data, retv, catalog, show=not runcontinuosly)
				
		if settings.t_on:
			temperature = read_temperature_from_device_uart(settings.baudrate, settings.port)
			print(temperature.t)
			
	except OSError as e:
		print(e)
	except RuntimeError as e:
		print(e)
	if runcontinuosly:
		global next_call
		next_call = next_call + settings.sleeptime
		print(str(datetime.datetime.now())[:-3] + ': Wait ' + "{:.2f}".format(next_call - time.time()) + ' seconds')
		threading.Timer(next_call - time.time(), ppm_measure).start()

ppm_measure()
