from typing import List
from math import ceil
from logging_system import LoggingSystem


class MemoryElement:
    def __init__(self, size):
        self.size = size
        self.occupied = False
        self.data = bytearray([0 for i in range(size)])


class PageUnit:
    def __init__(self, frame_number: int, page_id: int, process_id: int):
        self.frame_number = frame_number
        self.present_in_main_memory = False
        self.modified = False
        self.last_access_timestamp = 0
        self.page_id = page_id
        self.process_id = process_id


class ProcessPageCollection:
    def __init__(self):
        self.page_set: List[PageUnit] = []

    def initialize_pages(self, process_size: int, page_size: int, process_id):
        page_count = ceil(process_size / page_size)
        for page_index in range(page_count):
            LoggingSystem.log(f"▶ Creating page {page_index} in process page table")
            self.page_set.append(PageUnit(0, page_index, process_id))

    def remove_page(self, page):
        self.page_set.remove(page)

    def remove_page_by_index(self, page_number):
        self.page_set.pop(page_number) 