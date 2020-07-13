import requests
import sys

data = {'domain': open(sys.argv[1], 'r').read(),
		'problem': open(sys.argv[2], 'r').read()}

response = requests.post('http://solver.planning.domains/solve', json=data).json()

with open(sys.argv[3], 'w') as f:
	for act in response['result']['plan']:
		f.write(str(act['name']))
		f.write('\n')

# f = open("out.txt", 'r+')
# lines = f.readlines()
# f.close()

# print(lines)

# for i in range(len(lines)):
# 	if 'led' in lines[i]:
# 		if 'on' in lines[i]:
# 			print ("LED ON found!!")
# 			print ("Line number: {}".format(i))

# 	if 'door' in lines[i]:
# 		if 'open' in lines[i]:
# 			print ("Door Open found!!")
# 			print ("Line number: {}".format(i))

#print ("Success !!!")