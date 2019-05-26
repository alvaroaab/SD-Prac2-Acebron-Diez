import pika, os, random, json
import pywren_ibm_cloud as pywren

def leader_func(x):
	pw_config = json.loads(os.environ.get('PYWREN_CONFIG',''))
	connection = pika.BlockingConnection(pika.URLParameters(pw_config['rabbitmq']['amqp_url']))
	channel = connection.channel()
	channel.queue_declare('leader')
	slave_list = []
	while(len(slave_list) < int(x)):
		method, properties, body = channel.basic_get('leader')
		if(body != None):
			channel.basic_ack(delivery_tag = method.delivery_tag)
			slave_list.append(int(body.decode('utf-8')))

	channel.queue_declare('leader_finished')
	for i in range(len(slave_list)):
		index = random.randint(0, len(slave_list)-1)
		selected_slave = slave_list.pop(index)
		channel.queue_declare(str(selected_slave))
		channel.basic_publish(exchange = '', routing_key = str(selected_slave), body = 'Selected')
		body = ''
		while body != 'Finished':
			method, properties, body = channel.basic_get('leader_finished')
			if(body != None):
				body = body.decode('utf-8')

	channel.close()
	connection.close()
	return slave_list


def slave_func(id_slave, num_maps):
	pw_config = json.loads(os.environ.get('PYWREN_CONFIG',''))
	connection = pika.BlockingConnection(pika.URLParameters(pw_config['rabbitmq']['amqp_url']))
	channel = connection.channel()
	channel.queue_declare('leader')
	channel.basic_publish(exchange='',routing_key='leader',body=str(id_slave))
	channel.queue_declare(str(id_slave))
	finalList = []
	while(len(finalList) < num_maps):
		method, properties, body = channel.basic_get(str(id_slave))
		if(body != None):
			channel.basic_ack(delivery_tag = method.delivery_tag)
			if(body.decode('utf-8') == 'Selected'):
				num = random.randint(0,10)
				for i in range(num_maps):
					channel.queue_declare(str(i))
					channel.basic_publish(exchange = '', routing_key = str(i), body = str(num))
				#channel.exchange_declare(exchange='fanout', exchange_type='fanout')
				#channel.basic_publish(exchange='fanout',routing_key = '',body=str(num))
				channel.queue_declare('leader_finished')
				channel.basic_publish(exchange='',routing_key='leader_finished',body='Finished')

			else:
				finalList.append(int(body.decode('utf-8')))
	
	channel.close()
	connection.close()
	return finalList


pw_leader = pywren.ibm_cf_executor(rabbitmq_monitor=True)

num_maps = int(input("Introdueixi el numero de slaves: "))
data = []
for i in range(num_maps):
	data.append([i,num_maps])

print(data)

pw_leader.call_async(leader_func,num_maps)

pw_slave = pywren.ibm_cf_executor(rabbitmq_monitor=True)
pw_slave.map(slave_func, data)

print(pw_leader.get_result())
print(pw_slave.get_result())
pw_leader.clean()
pw_slave.clean()

