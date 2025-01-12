from dataclasses import dataclass
from datetime import datetime

from torrent_tracker_search.common.model.ISearchResultItem import ISearchResultItem
from torrent_tracker_search.source.nnmclub.model.NNMClubAuthorLink import NNMClubAuthorLink
from torrent_tracker_search.source.nnmclub.model.NNMClubForumLink import NNMClubForumLink
from torrent_tracker_search.source.nnmclub.model.NNMClubTopicLink import NNMClubTopicLink


@dataclass
class NNMClubSearchItem(ISearchResultItem):
	id: int  # id for download torrent file
	author: NNMClubAuthorLink
	forum: NNMClubForumLink
	topic: NNMClubTopicLink
	size: int
	seed_count: int
	leech_count: int
	added_at: datetime
	
	@staticmethod
	def empty(id: int):
		return NNMClubSearchItem(
			id=id,
			author=NNMClubAuthorLink(0, ""),
			forum=NNMClubForumLink(0, ""),
			topic=NNMClubTopicLink(0, ""),
			size=0,
			seed_count=0,
			leech_count=0,
			added_at=datetime.now()
		)
	