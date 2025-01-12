from datetime import datetime
from typing import List

from bs4 import BeautifulSoup, Tag

from torrent_tracker_search.common.TrackerSearchNotFoundException import TrackerSearchNotFoundException
from torrent_tracker_search.source.nnmclub.model.NNMClubAuthorLink import NNMClubAuthorLink
from torrent_tracker_search.source.nnmclub.model.NNMClubForumLink import NNMClubForumLink
from torrent_tracker_search.source.nnmclub.model.NNMClubSearchItem import NNMClubSearchItem
from torrent_tracker_search.source.nnmclub.model.NNMClubTopicLink import NNMClubTopicLink
from torrent_tracker_search.source.nnmclub.parser import get_forum_id, get_user_id, get_torrent_id, get_topic_id


class NNMClubSearchParser:
	
	@classmethod
	def parse(cls, html: str) -> List[NNMClubSearchItem]:
		if html.count("Не найдено") > 0:
			raise TrackerSearchNotFoundException()
		soup = BeautifulSoup(html, "html.parser")
		content_table = soup.find("table", attrs={"class": "forumline tablesorter"})
		result = list()
		for item_tr in content_table.tbody.childGenerator():
			if type(item_tr) is Tag:
				result.append(cls.parse_item(item_tr))
		return result
		
	@classmethod
	def parse_item(cls, item_tr: Tag) -> NNMClubSearchItem:
		items = [td for td in item_tr.find_all("td")]
		if len(items) == 10:
			_, forum_td, topic_td, author_td, torrent_td, size_td, seed_td, leech_td, reply_td, added_at_td = items
		elif len(items) == 11:
			_, forum_td, topic_td, author_td, torrent_td, size_td, _, seed_td, leech_td, reply_td, added_at_td = items
		else:
			raise Exception(f"Allowed only 10 items. Parser is broken. Now items count {len(items)}")

		forum = NNMClubForumLink(
			id=get_forum_id(forum_td),
			name=str(forum_td.text).strip("\n")
		)
		author = NNMClubAuthorLink(
			id=get_user_id(author_td),
			name=str(author_td.text).strip("\n")
		)
		return NNMClubSearchItem(
			id=get_torrent_id(torrent_td),
			topic=NNMClubTopicLink(
				id=get_topic_id(topic_td),
				name=topic_td.a.text,
			),
			author=author,
			forum=forum,
			size=int(size_td.u.text),
			seed_count=int(seed_td.text),
			leech_count=int(leech_td.text),
			added_at=datetime.fromtimestamp(int(added_at_td.u.text))
		)
