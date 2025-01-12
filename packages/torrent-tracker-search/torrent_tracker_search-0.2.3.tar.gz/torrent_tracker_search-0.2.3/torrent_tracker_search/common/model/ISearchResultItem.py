from datetime import datetime


class Link:
	id: int
	name: str
	

class ISearchResultItem:
	id: int  # id for download torrent file
	author: Link
	forum: Link
	topic: Link
	size: int
	seed_count: int
	leech_count: int
	added_at: datetime
	