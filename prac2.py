import pika, os, random, json
import pywren_ibm_cloud as pywren

def leader_func(x):
	pw_config = json.loads(os.environ.get('PYWREN_CONFIG',''))
	connection = pika.BlockingConnection(pika.URLParameters(pw_config['rabbitmq']['amqp_url']))
	channel = connection.channel()
	channel.queue_declare(queue='leader')
	channel.queue_declare(queue='leader_finished')
	slave_list = []

	while(len(slave_list) < int(x)):
		method, properties, body = channel.basic_get('leader')
		if(body != None):
			channel.basic_ack(method.delivery_tag)
			slave_list.append(int(body.decode('utf-8')))
	
	for i in range(len(slave_list)):
		index = random.randint(0, len(slave_list)-1)
		selected_slave = slave_list.pop(index)
		channel.queue_declare(queue=str(selected_slave))
		channel.basic_publish(exchange = '', routing_key = str(selected_slave), body = 'Selected')
		body = ''
		while(body!='Finished'):
			method, properties, body = channel.basic_get('leader_finished')
			if(body!=None):
				body = body.decode('utf-8')

	channel.queue_delete(queue='leader')
	channel.queue_delete(queue='leader_finished')
	channel.close()
	connection.close()

def slave_func(id_slave, num_maps):
	pw_config = json.loads(os.environ.get('PYWREN_CONFIG',''))
	connection = pika.BlockingConnection(pika.URLParameters(pw_config['rabbitmq']['amqp_url']))
	channel = connection.channel()

	channel.queue_declare(queue=str(id_slave))
	channel.queue_declare(queue='leader')
	channel.queue_declare(queue='leader_finished')
	channel.basic_publish(exchange='',routing_key='leader',body=str(id_slave))

	rand_list = []
	while(len(rand_list) < num_maps):
		method, properties, body = channel.basic_get(str(id_slave))
		if(body != None):
			channel.basic_ack(method.delivery_tag)
			if(body.decode('utf-8') == 'Selected'):
				num = random.randint(0,1000)
				for i in range(num_maps):
					channel.queue_declare(queue=str(i))
					channel.basic_publish(exchange = '', routing_key = str(i), body = str(num))
				channel.basic_publish(exchange = '', routing_key = 'leader_finished', body = 'Finished')
			else:
				rand_list.append(int(body.decode('utf-8')))

	channel.queue_delete(queue=str(id_slave))
	channel.close()
	connection.close()
	return rand_list



num_maps = int(input("Introdueixi el numero de slaves: "))
data = []
for i in range(num_maps):
	data.append([i,num_maps])

pw_leader = pywren.ibm_cf_executor(rabbitmq_monitor=True)
pw_leader.call_async(leader_func,num_maps)

pw_slave = pywren.ibm_cf_executor(rabbitmq_monitor=True)
pw_slave.map(slave_func, data)

print(pw_slave.get_result())
pw_leader.clean()
pw_slave.clean()

