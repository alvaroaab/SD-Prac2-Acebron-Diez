import pika, os
import pywren_ibm_cloud as pywren
from pywren_ibm_cloud import testpywren

def incrementa(x):
	return x+1

pw = pywren.ibm_cf_executor()
pw_config = json.loads(os.environ.get('PYWREN_CONFIG', ''))
pw.call_async(incrementa, 10)
results = pw.get_result()
print(results)
pw.map(incrementa, range(10))
results = pw.get_result()
print(results)
