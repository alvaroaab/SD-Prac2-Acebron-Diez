import pika, os, random, json
import pywren_ibm_cloud as pywren

def leader_func(x):
	pw_config = json.loads(os.environ.get('PYWREN_CONFIG',''))
	connection = pika.BlockingConnection(pika.URLParameters(pw_config['rabbitmq']['amqp_url']))

	channel = connection.channel()
	channel.declare(queue='leader')
	slave_list = [0,2,1,3]

	for i in range(x):
		method, properties, body = channel.basic_get('leader')
		channel.basic_ack(delivery_tag = method.delivery_tag)
		channel.queue_declare(queue = body)
		channel.basic_publish(exchange = '', routing_key = body, body = str(x))
		slave_list.append(body)

	for i in range(len(slave_list)):
		index = random.randint(0, len(slave_list)-1)
		selected_slave = slave_list.pop(index)
		channel.queue_declare(queue = selected_slave)
		channel.basic_publish(exchange = '', routing_key = selected_slave, body = '')

def slave_func(x):


pw_leader = pywren.ibm_cf_executor(rabbitmq_monitor=True)

num_maps = input("Introdueixi el numero de slaves")
ids= list(range(0,num_maps))

pw_leader.call_async(leader_func,num_maps)

pw_slave = pywren.ibm_cf_executor(rabbitmq_monitor=True)
pw_slave.map(slave_func, ids)

print(pw_slave.get_result())
pw_leader.clean()
pw_slave.clean()

