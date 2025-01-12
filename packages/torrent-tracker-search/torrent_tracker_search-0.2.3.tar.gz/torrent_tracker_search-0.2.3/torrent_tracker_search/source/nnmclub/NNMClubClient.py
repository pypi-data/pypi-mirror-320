from typing import Final, Optional

from torrent_tracker_search.common.TrackerClient import TrackerClient
from torrent_tracker_search.common.TrackerRequestException import TrackerRequestException
from torrent_tracker_search.common.TrackerResponse import TrackerResponse


class NNMClubClient(TrackerClient):
	BASE_URL: Final[str] = "https://nnmclub.to/forum"
	SESSION_COOKIE_KEY: Final[str] = "phpbb2mysql_4_sid"
	
	async def get(self, url: str, params: Optional[dict] = None, allow_redirects: bool = True) -> TrackerResponse:
		async with self.session.get(url=url, params=params, ssl=False, allow_redirects=allow_redirects) as response:
			success_status_code = 200 if allow_redirects else 302
			if response.status != success_status_code:
				raise TrackerRequestException()
			else:
				return TrackerResponse(
					headers=response.headers.copy(),
					status_code=response.status,
					body=await response.content.read()
				)
	
	async def post_form_data_encoded(self, url: str, body: dict, params: Optional[dict] = None, allow_redirects: bool = True) -> TrackerResponse:
		async with self.session.post(url=url, data=body, ssl=False, allow_redirects=allow_redirects, params=params) as response:
			success_status_code = 200 if allow_redirects else 302
			if response.status == success_status_code:
				return TrackerResponse(
					headers=response.headers.copy(),
					status_code=response.status,
					body=await response.content.read()
				)
			else:
				raise TrackerRequestException()
			
	async def post_form_data(self, url: str, body: dict, params: Optional[dict] = None, allow_redirects: bool = True) -> TrackerResponse:
		async with self.session.post(url=url, data=body, ssl=False, allow_redirects=allow_redirects, params=params) as response:
			success_status_code = 200 if allow_redirects else 302
			if response.status == success_status_code:
				return TrackerResponse(
					headers=response.headers.copy(),
					status_code=response.status,
					body=await response.content.read()
				)
			else:
				raise TrackerRequestException()
			