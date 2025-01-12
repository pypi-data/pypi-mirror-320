from dataclasses import dataclass
from typing import Dict

from multidict import CIMultiDict


@dataclass
class TrackerResponse:
	headers: CIMultiDict[str]
	status_code: int
	body: bytes
	
	@property
	def cookies(self) -> Dict[str, str]:
		cookies = {}
		cookie_string = getattr(self.headers, "cookies", "")
		if cookie_string == "":
			return cookies
		cookie_strings = cookie_string.split(";")
		for cookie_string in cookie_strings:
			cookie_name, cookie_value = cookie_string.split("=")
			cookie_name = cookie_name.strip()
			cookies[cookie_name] = cookie_value
		return cookies
	