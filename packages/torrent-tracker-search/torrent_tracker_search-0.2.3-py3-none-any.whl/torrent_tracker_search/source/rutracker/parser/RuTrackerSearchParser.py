from datetime import datetime
from typing import List

from bs4 import BeautifulSoup, Tag

from torrent_tracker_search.common.TrackerSearchNotFoundException import TrackerSearchNotFoundException
from torrent_tracker_search.source.rutracker.model.RuTrackerAuthorLink import RuTrackerAuthorLink
from torrent_tracker_search.source.rutracker.model.RuTrackerForumLink import RuTrackerForumLink
from torrent_tracker_search.source.rutracker.model.RuTrackerSearchItem import RuTrackerSearchItem
from torrent_tracker_search.source.rutracker.model.RuTrackerTopicLink import RuTrackerTopicLink
from torrent_tracker_search.source.rutracker.parser import get_forum_id, get_user_id, get_topic_id


class RuTrackerSearchParser:
	
	@staticmethod
	def items(html: str) -> List[RuTrackerSearchItem]:
		if html.count("Не найдено") > 0:
			raise TrackerSearchNotFoundException()
		soup = BeautifulSoup(html, "html.parser")
		content_table = soup.find("table", attrs={"id": "tor-tbl"})
		table_body = content_table.tbody
		result = []
		for item in table_body.childGenerator():
			if type(item) is Tag:
				result.append(RuTrackerSearchParser.item(item))
		return result
		
	@staticmethod
	def item(item: Tag) -> RuTrackerSearchItem:
		items = [td for td in item.find_all("td")]
		if len(items) == 10:
			id_td, is_verified_td, forum_td, torrent_td, author_td, size_td, seed_td, leech_td, download_td, added_at_td = items
			forum = RuTrackerForumLink(
				id=get_forum_id(forum_td),
				name=str(forum_td.text).strip("\n")
			)
			author = RuTrackerAuthorLink(
				id=get_user_id(author_td),
				name=str(author_td.text).strip("\n")
			)
			torrent_div, tags_div = torrent_td.find_all("div")
			return RuTrackerSearchItem(
				id=int(id_td["id"]),
				is_verified=is_verified_td.text == "√",
				topic=RuTrackerTopicLink(
					id=get_topic_id(torrent_div),
					name=str(torrent_div.text).strip("\n")
				),
				tags=[tag_span.text for tag_span in tags_div.childGenerator()],
				forum=forum,
				author=author,
				size=int(size_td["data-ts_text"]),
				seed_count=int(seed_td.text),
				leech_count=int(leech_td.text),
				download_count=int(download_td.text),
				added_at=datetime.fromtimestamp(int(added_at_td["data-ts_text"]))
			)
		else:
			raise Exception(f"Allowed only 10 items. Parser is broken. Now items count {len(items)}")
	