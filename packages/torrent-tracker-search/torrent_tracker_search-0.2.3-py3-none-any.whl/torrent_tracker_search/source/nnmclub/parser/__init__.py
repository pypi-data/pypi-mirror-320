from urllib.parse import urlparse

from bs4 import Tag


def get_query_param(source: Tag, param_key: str) -> str:
	source_href = source.a["href"]
	query = urlparse(source_href).query.split("&")
	for item in query:
		if item.startswith(f"{param_key}="):
			query_name, query_value = item.split("=")
			return query_value
	raise Exception(f"Error on get quert param from {source}")

def get_forum_id(forum_td: Tag) -> int:
	return int(get_query_param(forum_td,"f"))

def get_user_id(author_td: Tag) -> int:
	return int(get_query_param(author_td, "pid"))

def get_torrent_id(torrent_td: Tag) -> int:
	return int(get_query_param(torrent_td, "id"))

def get_topic_id(topic_td: Tag) -> int:
	return int(get_query_param(topic_td, "t"))
