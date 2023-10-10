import random
import re
import requests
from base64 import b64encode, b64decode
import json
# appid https://st.vk.com/dist/common.602753022377f6e91cb5.js?33521f26157b75f64ff4b0a (line 26019)
APPID = 7913379

def debug(localz):
	l = locals()
	for key, loc in localz.items():
		l[key] = loc
	while True:
		inp = input("(helper) >>> ")
		if inp == "exit":
			break
		try:
			print(eval(inp))
		except Exception as e:
			print(repr(e))

def get_uuid(iterations = 21):
	s = "ModuleSymbhasOwnPr-0123456789ABCDEFGHNRVfgctiUvz_KqYTJkLxpZXIjQW"
	return "".join([random.choice(s) for _ in range(iterations)])

def get_device_id(iterations = 21):
	s = "useandom-26T198340PX75pxJACKVERYMINDBUSHWOLF_GQZbfghjklqvwyzrict"
	return "".join([random.choice(s) for _ in range(iterations)])

class VKLoginHelper:
	def __init__(self):
		self.headers = {
			"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/116.0",
			"Host": "vk.com",
			"Origin": "https://vk.com",
			"Referer": "https://vk.com/"
		}
		self.post_headers = {
			"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/116.0",
			"Host": "vk.com",

			"Content-Type": "application/x-www-form-urlencoded",
			"X-Requested-With": "XMLHttpRequest"
		}
		self.session = requests.session()
		self.device_id = get_device_id()
		self.uuid = get_uuid()
		self.hash = self._re_get1("https://vk.com/", r"initVkId\(.*\"hash\"\:\"(\w+)\".*\)")
	def login(self, login, password, remember=True):
		self._real_login(login, password)
	def save_silent_token(self):
		...
	def login_silent(self, token):
		...
	def set_cookies(self, cookies : dict):
		self.session.cookies = requests.utils.cookiejar_from_dict(cookies)
	def get_cookies(self):
		return requests.utils.dict_from_cookiejar(self.session.cookies)
	def get(self, url, *args, **kvargs):
		return self._get_assert_json(url, *args, **kvargs)
	def post(self, url, data, *args, **kvargs):
		return self._post_assert_json(url, data, *args, **kvargs)

	# login functions
	def _real_login(self, login, password):
		token = self._get_login_token(login)
		auth_token = self._get_auth_token(token)
		login_proxy_url = self._get_login_redirect(auth_token, login, password)

		r = self._post_assert_response(login_proxy_url, {}, ref="https://id.vk.com")
		login_url = re.search(r"data-url=\"([^\"]+)\"", r.text).group(1).replace("&amp;", "&")
		# login_url_b64 = self._urlenc_get(login_proxy_url.split("?", 1)[1], "_to")
		# login_url = b64decode(login_url_b64).decode("utf8")

		login_php_r = self._post_assert_response(login_url, {}, ref="https://vk.com", expected_status_code=307, allow_redirects=False)
		rest_cookies_r = self._post_assert_response(login_php_r.headers["location"], {}, ref="https://vk.com", expected_status_code=307, allow_redirects=False)
		payload_r = self._post_assert_response(rest_cookies_r.headers["location"], {}, ref="https://vk.com", expected_status_code=200, allow_redirects=False)
		# restore_cookies_url = login_response.headers["location"]

	def _get_login_token(self, login):
		return self._post_assert_json(
			"https://vk.com/join.php?act=connect",
			{
				"al": 1,
				"expire": 0,
				"hash": self.hash,
				"login": login,
				"save_user": 1
			},
			ref = "https://vk.com"
		)["payload"][1][1]
	def _get_login_redirect(self, token, login, password):
		return self._post_assert_json(
			"https://login.vk.com/?act=connect_authorize",
			{
				"username": login,
				"password": password,
				"auth_token": token,
				"sid": "",
				"uuid": self.uuid,
				"v": "5.207",
				"device_id": self.device_id,
				"service_group": "",
				"agreement_hash": "",
				"oauth_force_hash": 0,
				"is_registration": 0,
				"oauth_response_type": "",
				"oauth_state": "",
				"expire": 0,
				"save_user": 1,
				"to": "aHR0cHM6Ly92ay5jb20vZmVlZD9wYXlsb2FkPSU3QiUyMnVzZXIlMjIlM0ElN0IlMjJmaXJzdF9uYW1lJTIyJTNBJTIyJTIyJTJDJTIybGFzdF9uYW1lJTIyJTNBJTIyJTIyJTdEJTdE",
				"version": 1,
				"app_id": APPID
			},
			ref = "https://id.vk.com"
		)["data"]["next_step_url"]
	def _get_auth_token(self, token):
		data = json.dumps({
			"name": "no_password_flow",
			"token": token,
			"params": {
				"type": "sign_in",
				"csrf_hash": self.hash
			}
		})
		b64data = b64encode(data.encode("ascii"))
		return self._re_get1(
			"https://id.vk.com/auth", r"\"access_token\":\"([\w\d\.\_\-]*)\"",
			ref = "https://vk.com",
			params = {
				"app_id": APPID,
				"response_type": "silent_token",
				"v": "1.60.6",
				"redirect_uri": "https://vk.com/feed",
				"uuid": self.uuid,
				"scheme": "space_gray",
				"action": b64data,
				"initial_stats_info": "eyJzb3VyY2UiOiJtYWluIiwic2NyZWVuIjoic3RhcnRfcHJvY2VlZF9hcyJ9"
			}
		)
	# challenge
	def _pass_challenge(self, url):
		pass

	# webpage getters
	def _post_assert_response(self, url, data, ref = None, expected_status_code=200, *args, **kvargs):
		headers = self.post_headers
		self._reference_headers(headers, url, ref)
		r = self.session.post(url, data, headers=headers, *args, **kvargs)
		print(r.status_code)
		assert r.status_code == expected_status_code
		return r
	def _get_assert_response(self, url, ref = None, expected_status_code=200, *args, **kvargs):
		headers = self.post_headers
		self._reference_headers(headers, url, ref)
		r = self.session.get(url, headers=headers, *args, **kvargs)
		assert r.status_code == expected_status_code
		return r
	def _reference_headers(self, headers, url, ref):
		headers.update({
			"Host": re.match(r"https?://([\w\.]+)", url).group(1)
		})
		if ref is not None:
			headers.update({
				"Referer": ref,
				"Origin": ref
			})
	def _post_assert_json(self, url, data, ref=None, *args, **kvargs):
		return self._post_assert_response(url, data, ref, *args, **kvargs).json()
	def _get_assert_json(self, url, ref=None, *args, **kvargs):
		return self._get_assert_response(url, ref, *args, **kvargs).json()
	# misc
	def _urlenc_get(self, url_encoded, key):
		data = dict(map(lambda v: v.split("="), url_encoded.split("&")))
		return data[key]
	def _re_get1(self, url, re_str, *args, **kvargs):
		r = self._get_assert_response(url, *args, **kvargs)
		mat = re.search(re_str, r.text)
		assert mat is not None
		return mat.group(1)