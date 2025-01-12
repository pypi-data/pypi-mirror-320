import base64
import json
from typing import Optional, List

from torrent_tracker_search.common.TorrentTracker import TorrentTracker
from torrent_tracker_search.common.TrackerClient import TrackerClient
from torrent_tracker_search.source.rutracker.RuTrackerClient import RuTrackerClient
from torrent_tracker_search.source.rutracker.model.RuTrackerSearchItem import RuTrackerSearchItem
from torrent_tracker_search.source.rutracker.model.RuTrackerTorrentFile import RuTrackerTorrentFile
from torrent_tracker_search.source.rutracker.model.RuTrackerTorrentItem import RuTrackerTorrentItem
from torrent_tracker_search.source.rutracker.parser.RuTrackerSearchParser import RuTrackerSearchParser
from torrent_tracker_search.source.rutracker.RuTrackerURL import RuTrackerURL
from torrent_tracker_search.source.rutracker.parser.RuTrackerTorrentFilesParser import RuTrackerTorrentFilesParser
from torrent_tracker_search.source.rutracker.parser.RuTrackerTorrentParser import RuTrackerTorrentParser


class RuTrackerService(TorrentTracker):
	
	def __init__(self, client: TrackerClient):
		self._client: TrackerClient = client
	
	async def search(self, query: str) -> List[RuTrackerSearchItem]:
		response = await self._client.get(
			url=RuTrackerURL.TRACKER.url,
			params={
				"nm": query
			}
		)
		body = response.body.decode("Windows-1251")
		return RuTrackerSearchParser.items(body)
	
	async def torrent(self, torrent_id: int) -> Optional[RuTrackerTorrentItem]:
		response = await self._client.get(
			url=RuTrackerURL.VIEW_TOPIC.url,
			params={
				"t": torrent_id
			}
		)
		body = response.body.decode("Windows-1251")
		torrent_dict = RuTrackerTorrentParser.parse(body)
		if torrent_dict is not None:
			form_token = RuTrackerTorrentParser.form_token(body)
			bb_code = await self.torrent_bb_code(post_id=torrent_dict["post_id"], form_token=form_token)
			if bb_code is not None:
				bb_code = base64.standard_b64encode(bb_code.encode()).decode()
			return RuTrackerTorrentItem(
				id=torrent_dict["torrent_id"],
				post_id=torrent_dict["post_id"],
				html_code=base64.standard_b64encode(torrent_dict["html_code"]).decode(),
				magnet_link=torrent_dict["magnet_link"],
				bb_code=bb_code,
				files=await self.torrent_files(torrent_id=torrent_id)
			)
		
	async def torrent_files(self, torrent_id: int) -> List[RuTrackerTorrentFile]:
		response = await self._client.post_form_data(
			url=RuTrackerURL.VIEW_TORRENT.url,
			body={
				"t": torrent_id
			}
		)
		body = response.body.decode("Windows-1251")
		return RuTrackerTorrentFilesParser.items(body)
	
	async def torrent_bb_code(self, post_id: int, form_token: str) -> Optional[str]:
		response = await self._client.post_form_data(
			url=RuTrackerURL.AJAX.url,
			body={
				"action": "view_post",
				"post_id": post_id,
				"mode": "text",
				"form_token": form_token
			}
		)
		body = response.body.decode()
		body_json: dict = json.loads(body)
		return body_json["post_text"]
		
	async def login_by_credentials(self, login: str, password: str) -> Optional[str]:
		response = await self._client.post_form_data_encoded(
			url=RuTrackerURL.LOGIN.url,
			body={
				"login_username": login,
				"login_password": password,
				"login": ""
			},
			allow_redirects=False
		)
		new_cookies = response.headers.getall("Set-Cookie")
		for new_cookie in new_cookies:
			if new_cookie.startswith(RuTrackerClient.SESSION_COOKIE_KEY):
				cookie_string = new_cookie.split(";")[0]
				cookie_name, cookie_value = cookie_string.split("=")
				self._client.session.cookie_jar.update_cookies({RuTrackerClient.SESSION_COOKIE_KEY: cookie_value})
				return cookie_value
		return None
	
	def login_by_session(self, session_id: str):
		self._client.session.cookie_jar.update_cookies({RuTrackerClient.SESSION_COOKIE_KEY: session_id})
