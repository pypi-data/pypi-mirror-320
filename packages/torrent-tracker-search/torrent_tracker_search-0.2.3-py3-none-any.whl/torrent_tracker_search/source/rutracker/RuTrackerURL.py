from enum import Enum

from torrent_tracker_search.source.rutracker.RuTrackerClient import RuTrackerClient


class RuTrackerURL(Enum):
	MAIN = "index.php"
	LOGIN = "login.php"
	TRACKER = "tracker.php"
	VIEW_TOPIC = "viewtopic.php"
	VIEW_TORRENT = "viewtorrent.php"
	AJAX = "ajax.php"
	
	@property
	def url(self) -> str:
		return f"{RuTrackerClient.BASE_URL}/{self.value}"
