from typing import List, Optional

from torrent_tracker_search.common.TorrentTracker import TorrentTracker
from torrent_tracker_search.common.model.ISearchResultItem import ISearchResultItem
from torrent_tracker_search.common.model.ITorrentItem import ITorrentItem
from torrent_tracker_search.source.nnmclub.NNMClubService import NNMClubService
from torrent_tracker_search.source.nnmclub.model.NNMClubSearchItem import NNMClubSearchItem
from torrent_tracker_search.source.rutracker.RuTrackerService import RuTrackerService
from torrent_tracker_search.source.rutracker.model.RuTrackerSearchItem import RuTrackerSearchItem


class TorrentTrackerSearch:
	
	def __init__(self, trackers: List[TorrentTracker]):
		self._trackers = trackers
	
	async def search(self, query: str) -> List[ISearchResultItem]:
		search_result = []
		for tracker in self._trackers:
			tracker_result = await tracker.search(query)
			for result in tracker_result:
				search_result.append(result)
		return search_result
		
	async def torrent(self, search_item: ISearchResultItem) -> Optional[ITorrentItem]:
		if type(search_item) is RuTrackerSearchItem:
			for tracker in self._trackers:
				if type(tracker) is RuTrackerService:
					return await tracker.torrent(search_item.id)
		if type(search_item) is NNMClubSearchItem:
			for tracker in self._trackers:
				if type(tracker) is NNMClubService:
					return await tracker.torrent(search_item.id)
		return None
	