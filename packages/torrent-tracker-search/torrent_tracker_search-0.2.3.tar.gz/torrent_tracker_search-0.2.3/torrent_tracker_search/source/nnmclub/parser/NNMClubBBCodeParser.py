from typing import Optional

from bs4 import BeautifulSoup


class NNMClubBBCodeParser:
	
	@classmethod
	def parse(cls, html: str) -> Optional[str]:
		soup = BeautifulSoup(html, "html.parser")
		textarea = soup.find("textarea")
		if textarea is not None:
			return textarea.text
		else:
			return None
