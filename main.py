from vk_login_helper import VKLoginHelper
from playlist import VKPlaylist
from datetime import datetime
import json
from random import randint
from time import perf_counter, sleep

def login_all(cookies_fp):
	if not (cookies_fp.mode != "w" or cookies_fp.mode != "r+" or cookies_fp.mode != "a+"):
		raise TypeError("cookies_fp.mode must be 'w', 'r+' or 'a+'")
	helpers = []
	with open("accounts.txt", "r") as accounts_fp:
		for line in accounts_fp:
			try:
				helper = VKLoginHelper()
				login, passwd = line.split(" ", 1)
				print(login, passwd)
				helper.login(login, passwd)
				helpers.append(helper)
				cookies_fp.write("{0}\n".format(json.dumps(helper.get_cookies())))
			except Exception as e:
				print(f"account '{line}' failed to login")
				print(repr(e))
	return helpers
	
def main():
	...

SLEEP_TIME = 60
if __name__ == "__main__":
	login_helpers = []
	try:
		with open("cookies.txt", "r+") as f:
			date = f.readline()[:-1]
			if date != datetime.now().strftime("%D"):
				login_helpers = login_all(f)
			else:
				# already logged on today
				for line in f:
					helper = VKLoginHelper()
					helper.set_cookies(json.loads(line))
					login_helpers.append(helper)
	except FileNotFoundError:
		with open("cookies.txt", "w") as f:
			f.write("{0}\n".format(datetime.now().strftime("%D")))
			login_helpers = login_all(f)
	if not login_helpers:
		print("Accounts list empty")
		exit(-1)

	with open("playlist.txt", "r") as f:
		playlist_url = f.readline()
	playlist = VKPlaylist.from_url(playlist_url, login_helpers[0])

	start_listens = playlist.listens
	fake_listens_start = 0
	fake_listens = 0
	listens_start = perf_counter()
	print(f"Listens: {start_listens}")
	while True:
		start = perf_counter()
		fake_listens_start = fake_listens
		for helper in login_helpers:
			playlist.bind_login_helper(helper)
			playlist.listen_item(randint(0, 1))
			fake_listens += 1
		end = perf_counter()
		delta = end - start
		sleep_time = max(0, SLEEP_TIME - delta)

		print(f"Total: {fake_listens}")
		print(f"Total time: {(end - listens_start):.1f} minutes")
		print(f"Speed: {(fake_listens - fake_listens_start) / (SLEEP_TIME / 60):.2f} listens/minute")
		print(f"Sleeping for {sleep_time:.2f}s")
		sleep(sleep_time)