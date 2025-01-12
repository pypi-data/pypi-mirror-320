from dataclasses import dataclass
from datetime import datetime
from typing import List

from torrent_tracker_search.common.model.ISearchResultItem import ISearchResultItem
from torrent_tracker_search.source.rutracker.model.RuTrackerAuthorLink import RuTrackerAuthorLink
from torrent_tracker_search.source.rutracker.model.RuTrackerForumLink import RuTrackerForumLink
from torrent_tracker_search.source.rutracker.model.RuTrackerTopicLink import RuTrackerTopicLink


@dataclass
class RuTrackerSearchItem(ISearchResultItem):
	id: int  # id for download torrent file
	is_verified: bool
	topic: RuTrackerTopicLink
	author: RuTrackerAuthorLink
	forum: RuTrackerForumLink
	tags: List[str]
	size: int
	seed_count: int
	leech_count: int
	download_count: int
	added_at: datetime
	
	@staticmethod
	def empty(id: int):
		return RuTrackerSearchItem(
			id=id,
			is_verified=False,
			topic=RuTrackerTopicLink(0, ""),
			author=RuTrackerAuthorLink(0, ""),
			forum=RuTrackerForumLink(0, ""),
			tags=[],
			size=0,
			seed_count=0,
			leech_count=0,
			download_count=0,
			added_at=datetime.now()
		)
	