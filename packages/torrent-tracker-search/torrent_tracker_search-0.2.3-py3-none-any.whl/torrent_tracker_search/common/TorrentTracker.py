from typing import Optional, List

from torrent_tracker_search.common.model.ISearchResultItem import ISearchResultItem
from torrent_tracker_search.common.model.ITorrentItem import ITorrentItem


class TorrentTracker:
	
	async def search(self, query: str) -> List[ISearchResultItem]: ...
	
	async def torrent(self, topic_id: int) -> Optional[ITorrentItem]: ...
