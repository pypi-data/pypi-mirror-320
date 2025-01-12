from typing import Optional

from bs4 import BeautifulSoup, Tag

from torrent_tracker_search.source.nnmclub.parser import get_torrent_id


class NNMClubTorrentParser:
	
	@classmethod
	def parse(cls, html: str) -> Optional[dict]:
		soup = BeautifulSoup(html, "html.parser")
		table = soup.find("th", string="Сообщение").find_parent("table")
		tables = [tag for tag in table.childGenerator() if type(tag) is Tag]
		content_table = [tag for tag in tables[1].childGenerator() if type(tag) is Tag][1].table
		if content_table is not None:
			items = [tag for tag in content_table.childGenerator() if type(tag) is Tag]
			header, _, torrent_page, torrent_details, _ = items
			magnet_link = torrent_details.find("a", attrs={"title": "Примагнититься"})
			torrent_id_a = torrent_details.find("a", string="Скачать")
			torrent_id = get_torrent_id(torrent_id_a.parent)
			return {
				"id": int(torrent_id),
				"post_id": int(content_table["id"].replace("post_", "")),
				"html_code": torrent_page,
				"magnet_link": magnet_link["href"]
			}
		else:
			return None
		