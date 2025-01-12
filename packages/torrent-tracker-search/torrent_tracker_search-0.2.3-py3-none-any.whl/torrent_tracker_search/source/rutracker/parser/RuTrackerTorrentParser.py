import json
from typing import Optional

from bs4 import BeautifulSoup


class RuTrackerTorrentParser:
	
	@staticmethod
	def form_token(html: str) -> str:
		form_token_start_index = html.index("form_token")
		form_token_end_index = html[form_token_start_index:].index(",")
		raw_form_token = html[form_token_start_index:form_token_start_index+form_token_end_index]
		form_token = raw_form_token.strip().replace("form_token: ", "").replace("'", "")
		return form_token
	
	@staticmethod
	def parse(html: str) -> Optional[dict]:
		soup = BeautifulSoup(html, "html.parser")
		torrent_html = soup.find("div", attrs={"class": "post_body"})
		if torrent_html is not None:
			props = json.loads(torrent_html["data-ext_link_data"])
			post_id = int(props["p"])
			torrent_id = int(props["t"])
			magnet_link_a = soup.find("a", attrs={"data-topic_id": torrent_id})
			magnet_link = magnet_link_a["href"]
			return {
				"post_id": post_id,
				"torrent_id": torrent_id,
				"magnet_link": magnet_link,
				"html_code": torrent_html.encode()
			}
