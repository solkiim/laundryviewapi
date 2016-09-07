# a laundryview api based on https://github.com/RitwikGupta/PittAPI
# edited to be applicable to all laundryview users

import urllib2
import subprocess
import re

class LaundryAPI:
	def __init__(self):
		pass

	def get_status_detailed(self, room_id):
		# Get a cookie
		cookie_cmd = "curl -I -s \"http://www.laundryview.com/laundry_room.php?view=c&lr={}\"".format(room_id)

		response = subprocess.check_output(cookie_cmd, shell=True)
		response = response[response.index('Set-Cookie'):]
		cookie = response[response.index('=') + 1:response.index(';')]

		# Get the weird laundry data
		cmd = """
		curl -s "http://www.laundryview.com/dynamicRoomData.php?location={}" -H "Cookie: PHPSESSID={}" --compressed
		""".format(room_id, cookie)

		response = subprocess.check_output(cmd, shell=True)
		resp_split = response.split('&')[3:]

		cleaned_resp = []
		for status_string in resp_split:
			machine_name = status_string[:status_string.index('=')].replace('Status', '')
			status_string = status_string[status_string.index('=') + 1:].strip()

			machine_split = status_string.split("\n")
			machine_split[0] += machine_name

			try:
				machine_split[1] += machine_name
			except IndexError:
				pass

			machine_split = map(lambda x: x.split(':'), machine_split)
			cleaned_resp.append(machine_split[0])
			try:
				cleaned_resp.append(machine_split[1])
			except IndexError:
				pass

		cleaned_resp = filter(lambda x: len(x) == 10, cleaned_resp)
		
		di = []
		for machine in cleaned_resp:
			time_left = -1
			machine_name = "{}_{}".format(machine[9], machine[3])
			machine_status = ""
			
			if machine[0] is '1':
				machine_status = 'Free'
			else:
				if machine[6] is '':
					machine_status = 'Out of service'
				else:
					machine_status = 'In use'
					
			if machine_status is 'In use':
				time_left = int(machine[1])
			else:
				time_left = -1 if machine[6] is '' else machine[6]
			
			di.append({
				'machine_name': machine_name,
				'machine_status': machine_status,
				'time_left': time_left
			})
			
		return di
