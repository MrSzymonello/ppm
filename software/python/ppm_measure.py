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
from ppm_toolbox import save_raw_data
from ppm_toolbox import save_results


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

			# save results
			catalog = settings.datacatalog + raw_data.starttime.strftime("%Y%m%d")
			save_raw_data(catalog, raw_data)
			save_results(catalog, raw_data, retv)

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
