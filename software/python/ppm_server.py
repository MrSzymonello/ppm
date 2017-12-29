import ppm_settings as settings

import datetime
import sys
import warnings
import os

from ppm_toolbox import analyze_ppm
from ppm_toolbox import decode_from_base64
from ppm_toolbox import plot_results
from ppm_toolbox import save_raw_data
from ppm_toolbox import save_results
from ppm_toolbox import Logger
from scipy.optimize import OptimizeWarning

warnings.filterwarnings('error', category=RuntimeWarning)
warnings.filterwarnings("error", category=OptimizeWarning)

sys.stderr = Logger(sys.stderr, os.path.join(settings.datacatalog, datetime.datetime.utcnow().strftime("%Y%m%d")))

samplerate = float(sys.argv[1])
adcstarttimestamp = float(sys.argv[2])

isValid = True

try:
	raw_data = decode_from_base64(sys.stdin.read(), samplerate, adcstarttime = datetime.datetime.utcfromtimestamp(adcstarttimestamp))

	# save raw data
	catalog = settings.datacatalog + datetime.datetime.utcfromtimestamp(raw_data.starttime).strftime("%Y%m%d")
	sys.stderr.set_catalog(catalog) # keep logger updated to handle day change at UTC midnight
	file = save_raw_data(catalog, raw_data)

	# analyze
	retv = analyze_ppm(raw_data.voltagesamples, raw_data.samplerate, fitrangepct=[4.0, 90.0])

	if retv.t0 <= 0 or retv.t0 > 5:
		print(file + ' skipped, t0 = ' + str(retv.t0), file=sys.stderr)
		isValid = False

	if retv.t0_error > 1:
		print(file + ' skipped, t0_error = ' + str(retv.t0_error), file=sys.stderr)
		isValid = False

	if retv.x0_error > 1:
		print(file + ' skipped, x0_error = ' + str(retv.x0_error), file=sys.stderr)
		isValid = False

	if retv.f_error > 1:
		print(file + ' skipped, f_error = ' + str(retv.f_error), file=sys.stderr)
		isValid = False

	if isValid == True:
		# this message will be intercepted by a server process (Node or ASP.NET Core)
		print('OK\t' + 
			'{0:.2f}\t'.format(retv.B) +
			'{0:.2f}\t'.format(retv.frezfit) +
			'{0:.2f}\t'.format(retv.frezfft) +
			'{0:.2f}\t'.format(retv.t0) +
			'{0:.2f}\t'.format(retv.frezfft_amplitude) +
			'{0:.2f}\t'.format(retv.A) +
			'{:.2E}\t'.format(retv.x0_error) +
			'{:.2E}\t'.format(retv.f_error) +
			'{:.2E}\t'.format(retv.t0_error) +
			'{:.2E}\t'.format(retv.A_error) +
			'{:.2E}\t'.format(retv.y0_error) +
			'{}'.format(len(raw_data.voltagesamples)), file=sys.stdout)
	
		# save analysis results
		save_results(catalog, raw_data, retv)

		# plot results
		if settings.plot:
			plot_results(raw_data, retv, catalog, show=False)			
	else:
		print('ERROR')

except RuntimeError as e:
	print('ERROR')
	# RuntimeError: Optimal parameters not found
	print(file + ' skipped, ' + e.__str__(), file=sys.stderr)
except OptimizeWarning as e:
	# OptimizeWarning: Covariance of the parameters could not be estimated
	print('ERROR')
	print(file + ' skipped, ' + e.__str__(), file=sys.stderr)
except RuntimeWarning as e:
	# RuntimeWarning: overflow encountered in exp
	print('ERROR')
	print(file + ' skipped, ' + e.__str__(), file=sys.stderr)


