from typing import Optional, List

from torrent_tracker_search.common.model.ITorrentFile import ITorrentFile


class ITorrentItem:
	id: int
	post_id: int
	html_code: str
	magnet_link: str
	bb_code: Optional[str] = None
	files: Optional[List[ITorrentFile]] = None
