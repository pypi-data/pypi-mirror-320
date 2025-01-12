from enum import Enum

from torrent_tracker_search.source.nnmclub.NNMClubClient import NNMClubClient


class NNMClubURL(Enum):
	MAIN = "index.php"
	TRACKER = "tracker.php"
	POSTING = "posting.php"
	VIEW_TOPIC = "viewtopic.php"
	FILE_LIST = "filelst.php"
	
	@property
	def url(self) -> str:
		return f"{NNMClubClient.BASE_URL}/{self.value}"
