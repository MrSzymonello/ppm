import matplotlib
matplotlib.use('Agg')

import datetime
import sys
import warnings
import os
import getopt

from ppm_toolbox import analyze_ppm
from ppm_toolbox import decode_from_base64
from ppm_toolbox import plot_results
from ppm_toolbox import save_raw_data
from ppm_toolbox import save_results
from ppm_toolbox import Logger
from scipy.optimize import OptimizeWarning

warnings.filterwarnings('error', category=RuntimeWarning)
warnings.filterwarnings("error", category=OptimizeWarning)

dataCatalog = 'data'
savePlot = False
saveRaw = False
saveSummary = False
saveError = False

opts, args = getopt.getopt(sys.argv[1:], "d:prse", ["dataCatalog=", "plot", "raw", "summary", "error"])

sampleRate = float(args[0])
adcStartTime = float(args[1])

for o, a in opts:
	if o in ("-d", "--datacatalog"):
		dataCatalog = a
	elif o in ("-p", "--plot"):
		savePlot = True
	elif o in ("-r", "--raw"):
		saveRaw = True
	elif o in ("-s", "--summary"):
		saveSummary = True
	elif o in ("-e", "--error"):
		saveError = True

base64Samples = sys.stdin.read()

if saveError:
	sys.stderr = Logger(sys.stderr, os.path.join(dataCatalog, datetime.datetime.utcnow().strftime("%Y%m%d")))

def process(base64Samples, sampleRate, adcStartTime, dataCatalog, plot, raw, summary, error):

	isValid = True
	
	raw_data = decode_from_base64(base64Samples, sampleRate, adcstarttime = datetime.datetime.utcfromtimestamp(adcStartTime))

	# save raw data
	catalog = os.path.join(dataCatalog, datetime.datetime.utcfromtimestamp(raw_data.starttime).strftime("%Y%m%d"))
	if error:
		sys.stderr.set_catalog(catalog) # keep logger updated to handle day change at UTC midnight
	name = datetime.datetime.utcfromtimestamp(raw_data.starttime).strftime("%Y%m%d_%H%M%S_%f")[:-3]
	if raw:
		save_raw_data(catalog, raw_data)

	try:
		# analyze
		retv = analyze_ppm(raw_data.voltagesamples, raw_data.samplerate, fitrangepct=[4.0, 90.0])

	except RuntimeError as e:
		print('ERROR')
		# RuntimeError: Optimal parameters not found
		print(name + ' skipped, ' + e.__str__(), file=sys.stderr)
		return
	except OptimizeWarning as e:
		# OptimizeWarning: Covariance of the parameters could not be estimated
		print('ERROR')
		print(name + ' skipped, ' + e.__str__(), file=sys.stderr)
		return
	except RuntimeWarning as e:
		# RuntimeWarning: overflow encountered in exp
		print('ERROR')
		print(name + ' skipped, ' + e.__str__(), file=sys.stderr)
		return

	if retv.t0 <= 0 or retv.t0 > 5:
		print(name + ' skipped, t0 = ' + str(retv.t0), file=sys.stderr)
		isValid = False

	if retv.t0_error > 1:
		print(name + ' skipped, t0_error = ' + str(retv.t0_error), file=sys.stderr)
		isValid = False

	if retv.x0_error > 1:
		print(name + ' skipped, x0_error = ' + str(retv.x0_error), file=sys.stderr)
		isValid = False

	if retv.f_error > 1:
		print(name + ' skipped, f_error = ' + str(retv.f_error), file=sys.stderr)
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
		if summary:
			save_results(catalog, raw_data, retv)

		# plot results
		if plot:
			plot_results(raw_data, retv, catalog, show=False)			
	else:
		print('ERROR')

process(base64Samples, sampleRate, adcStartTime, dataCatalog, savePlot, saveRaw, saveSummary, saveError)
