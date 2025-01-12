import os
from typing import List, Optional

from bs4 import BeautifulSoup, Tag

from torrent_tracker_search.source.nnmclub.model.NNMClubTorrentFile import NNMClubTorrentFile


class NNMClubTorrentFilesParser:
	
	@classmethod
	def parse(cls, html: str) -> Optional[NNMClubTorrentFile]:
		soup = BeautifulSoup(html, "html.parser")
		items: List[NNMClubTorrentFile] = []
		content_table = soup.find("table")
		if content_table is None:
			return None
		for item in content_table.tbody.childGenerator():
			if type(item) is Tag:
				cls.parse_item(item, items)
		root_folder = items[0]
		f = cls.reassemble_to_folders(items[1:])
		root_folder.files = f.files
		cls.calculate_folder_size(root_folder)
		return root_folder
	
	@classmethod
	def calculate_folder_size(cls, folder: NNMClubTorrentFile):
		"""Calculate the total size of the folder by summing up the sizes of contained files and subfolders."""
		if not folder.is_folder:
			return folder.size
		
		total_size = 0
		for file in folder.files:
			if file.is_folder:
				total_size += cls.calculate_folder_size(file)
			else:
				total_size += file.size
		folder.size = total_size
		return folder.size
	
	@classmethod
	def reassemble_to_folders(cls, file_list):
		def add_file_to_folder(folder, path_parts, size):
			if not path_parts:
				return
			
			current_part = path_parts[0]
			remaining_parts = path_parts[1:]
			folder_dict = {file.name: file for file in folder.files}
			
			if current_part not in folder_dict:
				# If this part of the path is not in the folder, add it
				if remaining_parts:
					# If there are remaining parts, it's a folder
					new_folder = NNMClubTorrentFile(name=current_part, is_folder=True, files=[], size=0)
					folder.files.append(new_folder)
					add_file_to_folder(new_folder, remaining_parts, size)
				else:
					# If there are no remaining parts, it's a file
					new_file = NNMClubTorrentFile(name=current_part, is_folder=False, size=size, files=[])
					folder.files.append(new_file)
			else:
				# If the folder exists, continue adding the remaining path
				add_file_to_folder(folder_dict[current_part], remaining_parts, size)
		
		root_folder = NNMClubTorrentFile(name='root', is_folder=True, files=[], size=0)
		
		for file in file_list:
			path_parts = file.name.split(os.sep)
			add_file_to_folder(root_folder, path_parts, file.size)
		
		return root_folder
	
	@classmethod
	def parse_item(cls, tr_code: Tag, items: list):
		number, name, size_in_bytes, size_in_bites = list(tr_code.childGenerator())
		if number.text.strip() == "Папка":
			items.append(
				NNMClubTorrentFile(
					name=name.text.strip(),
					is_folder=True,
					files=[],
					size=0
				)
			)
		else:
			items.append(
				NNMClubTorrentFile(
					name=name.text.strip(),
					is_folder=False,
					files=[],
					size=int(size_in_bites.text.replace(",", ""))
				)
			)
		