from dataclasses import dataclass
from typing import Optional, List

from torrent_tracker_search.common.model.ITorrentItem import ITorrentItem
from torrent_tracker_search.source.nnmclub.model.NNMClubTorrentFile import NNMClubTorrentFile


@dataclass
class NNMClubTorrentItem(ITorrentItem):
	id: int
	post_id: int
	html_code: str
	magnet_link: str
	bb_code: Optional[str] = None
	files: Optional[List[NNMClubTorrentFile]] = None
