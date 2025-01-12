from typing import List, Optional

from torrent_tracker_search.common.TorrentTracker import TorrentTracker
from torrent_tracker_search.common.TrackerClient import TrackerClient
from torrent_tracker_search.source.nnmclub.NNMClubClient import NNMClubClient
from torrent_tracker_search.source.nnmclub.NNMClubURL import NNMClubURL
from torrent_tracker_search.source.nnmclub.model.NNMClubSearchItem import NNMClubSearchItem
from torrent_tracker_search.source.nnmclub.model.NNMClubTorrentFile import NNMClubTorrentFile
from torrent_tracker_search.source.nnmclub.model.NNMClubTorrentItem import NNMClubTorrentItem
from torrent_tracker_search.source.nnmclub.parser.NNMClubBBCodeParser import NNMClubBBCodeParser
from torrent_tracker_search.source.nnmclub.parser.NNMClubSearchParser import NNMClubSearchParser
from torrent_tracker_search.source.nnmclub.parser.NNMClubTorrentFilesParser import NNMClubTorrentFilesParser
from torrent_tracker_search.source.nnmclub.parser.NNMClubTorrentParser import NNMClubTorrentParser


class NNMClubService(TorrentTracker):
	
	def __init__(self, client: TrackerClient):
		self._client: TrackerClient = client
	
	async def search(self, query: str) -> List[NNMClubSearchItem]:
		response = await self._client.get(
			url=NNMClubURL.TRACKER.url,
			params={
				"nm": query,
				"f": "-1",
				"search_submit": ""
			}
		)
		body = response.body.decode("Windows-1251")
		return NNMClubSearchParser.parse(body)
		
	def login(self, session_id: str):
		self._client.session.cookie_jar.update_cookies({NNMClubClient.SESSION_COOKIE_KEY: session_id})
	
	async def torrent_files(self, torrent_id: int) -> Optional[NNMClubTorrentFile]:
		response = await self._client.get(
			url=NNMClubURL.FILE_LIST.url,
			params={
				"attach_id": torrent_id
			}
		)
		return NNMClubTorrentFilesParser.parse(response.body.decode("Windows-1251"))
	
	async def torrent_bb_code(self, torrent_post_id: int) -> Optional[str]:
		response = await self._client.get(
			url=NNMClubURL.POSTING.url,
			params={
				"mode": "quote",
				"p": torrent_post_id
			}
		)
		return NNMClubBBCodeParser.parse(response.body.decode("Windows-1251"))
	
	async def torrent(self, topic_id: int) -> Optional[NNMClubTorrentItem]:
		response = await self._client.get(
			url=NNMClubURL.VIEW_TOPIC.url,
			params={
				"t": topic_id
			}
		)
		data = NNMClubTorrentParser.parse(response.body.decode("Windows-1251"))
		if data is not None:
			return NNMClubTorrentItem(
				id=data["id"],
				post_id=data["post_id"],
				html_code=data["html_code"],
				magnet_link=data["magnet_link"],
				bb_code=await self.torrent_bb_code(torrent_post_id=data["post_id"]),
				files=await self.torrent_files(torrent_id=data["id"])
			)
		else:
			return None
