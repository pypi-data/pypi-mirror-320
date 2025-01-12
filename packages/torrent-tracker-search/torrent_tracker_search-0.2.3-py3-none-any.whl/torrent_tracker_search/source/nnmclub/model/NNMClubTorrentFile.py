from dataclasses import dataclass

from torrent_tracker_search.common.model.ITorrentFile import ITorrentFile


@dataclass
class NNMClubTorrentFile(ITorrentFile):
	name: str
	is_folder: bool
	files: list
	size: int
	