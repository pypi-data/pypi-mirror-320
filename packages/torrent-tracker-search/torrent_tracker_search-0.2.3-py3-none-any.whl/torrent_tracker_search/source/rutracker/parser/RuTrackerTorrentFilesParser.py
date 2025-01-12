from typing import List

from bs4 import BeautifulSoup

from torrent_tracker_search.source.rutracker.model.RuTrackerTorrentFile import RuTrackerTorrentFile


class RuTrackerTorrentFilesParser:
	
	@staticmethod
	def items(html: str) -> List[RuTrackerTorrentFile]:
		soup = BeautifulSoup(html, "html.parser")
		return RuTrackerTorrentFilesParser.parse_tree(soup.ul)
		
	@staticmethod
	def parse_tree(element):
		# Здесь мы собираем информацию обо всех элементах
		data = []
		if element.name == 'li':
			# sub_data = {}
			div = element.find('div')
			if div:
				# Получаем название
				name = div.find('b').text
				# sub_data['name'] = name
				# Получаем возможный идентификатор
				size = div.find('i')
				if size:
					size = int(size.text)
				else:
					size = 0
				
				data.append(RuTrackerTorrentFile(
					name=name,
					size=size,
					files=[],
					is_folder=False
				))
			
			# Обработка вложенного списка
			nested_ul = element.find('ul')
			if nested_ul:
				nested_data = RuTrackerTorrentFilesParser.parse_tree(nested_ul)
				if nested_data:
					new_size = data[-1].size
					for file in nested_data:
						new_size += file.size
					data[-1].is_folder = True
					data[-1].size = new_size
					data[-1].files = nested_data  # Добавляем дочерние элементы
		
		elif element.name == 'ul':
			for li in element.find_all('li', recursive=False):
				data.extend(RuTrackerTorrentFilesParser.parse_tree(li))
		
		return data
	