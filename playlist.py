from vk_login_helper import VKLoginHelper
import re
import random


def debug(localz):
	l = locals()
	for key, loc in localz.items():
		l[key] = loc
	while True:
		inp = input("(playlist) >>> ")
		if inp == "exit":
			break
		try:
			print(eval(inp))
		except Exception as e:
			print(repr(e))

def audio_tuple_to_dict(audio_tuple):
		audio_indexes = [
			"id",
			"owner_id",
			"url",
			"title",
			"performer",
			"duration",
			"album_id",
			"unk",
			"author_link",
			"lyrics",
			"flags",
			"context",
			"extra",
			"hashes",
			"cover_url",
			"ads",
			"subtitle",
			"main_artists",
			"feat_artists",
			"album",
			"track_code",
			"restriction",
			"album_part",
			"unk2",
			"access_key",
			"chart_info",
			"track_page_id",
			"is_original_sound"
		]

		return dict(zip(audio_indexes, audio_tuple))

class VKPlaylist:
	_PLAYLIST_URL_RE = r"https?://vk.com/(?P<location>audios(?P<id>\d+)\?z=audio_playlist(?P<owner_id>-?\d+)_(?P<playlist_id>\d+)(?:/(?P<access_hash>[\d\w]+))?)"
					   #r"|https://vk.com/music/playlist/(?P<owner_id>\d+)_(?<playlist_id>\d+)_49a5ea16e8f9b11886"
	def __init__(self, id, owner_id, playlist_id, location = None, access_hash = None, login_helper = None):
		if access_hash is None:
			access_hash = ""
		if location is None:
			location = ""
		self._access_hash = access_hash
		self._location = location
		self._login_helper = login_helper

		self.id = id
		self.owner_id = owner_id
		self.playlist_id = playlist_id
		self.title = ""
		self.description = ""
		self.items = []

		self._init_playlist_data()
	def bind_login_helper(self, login_helper):
		self._login_helper = login_helper
	def al_post(self, body, params = None):
		if self._login_helper is None:
			raise Exception("Please bind login_helper before using \"get()\"")
		return self._login_helper.post(
			"https://vk.com/al_audio.php",
			data = body,
			params = params,
		)
	def listen_item(self, index):
		item = self.items[index]
		payload = self.al_post(
			body = {
				"act": "listened_data",
	            "al": 1,
	            "audio_id": f'{item["owner_id"]}_{item["id"]}', 
	            "context": "",
	            "end_stream_reason": "stop_btn",
	            "hash":item["hashes"].rsplit("/", 2)[1],
	            "impl": "html5",
	            "listened": random.randint(1, 20),
	            "loc": self._location,
	            "playlist_id": f'{self.owner_id}_{self.playlist_id}{f"_{self._access_hash}" if self._access_hash else ""}',
	            "state": "app",
	            # "timings": 776,
	            "track_code": item["track_code"],
	            "v": "5"
			}
		)["payload"]
	def _init_playlist_data(self):
		payload = self.al_post(
			body = {
				"access_hash": self._access_hash,
				"al": 1,
				"claim": 0,
				"context": "",
				"from_id": self.id,
				"is_loading_all": 1,
				"is_preload": 0,
				"offset": 0,
				"owner_id": self.owner_id,
				"playlist_id": self.playlist_id,
				"type": "playlist"
			},
			params = {
				"act": "load_section"
			}
		)["payload"]
		if payload[0] != 0:
			raise Exception("Post error")
		playlist_info = payload[1][0]

		self.title = playlist_info["title"]
		self.description = playlist_info["description"]
		self.listens = int(playlist_info["listens"])
		self.items = list(map(audio_tuple_to_dict, playlist_info["list"]))
	@staticmethod
	def from_url(url, login_helper = None):
		mat = re.match(VKPlaylist._PLAYLIST_URL_RE, url)
		if mat is None:
			return None
		return VKPlaylist(**mat.groupdict(), login_helper = login_helper)
