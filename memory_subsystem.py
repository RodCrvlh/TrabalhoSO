from typing import List
from math import ceil
from logging_system import LoggingSystem
from paging_system import PageUnit, MemoryElement


class MainMemoryManager:
    def __init__(self, total_memory_size, frame_size):
        self.next_available_index = 0
        self.frame_structure: List[MemoryElement] = []
        self._initialize_frames(total_memory_size, frame_size)

    def _initialize_frames(self, total_memory_size, frame_size):
        frame_count = total_memory_size // frame_size
        LoggingSystem.log(
            f"🏗️ Structuring memory: {total_memory_size} bytes divided into {frame_count} frames of {frame_size} bytes each.")
        for index in range(frame_count):
            self.frame_structure.append(MemoryElement(frame_size))

    def allocate_space(self, page: PageUnit, current_cycle):
        frame_index, candidate_frame = self.get_next_frame()
        search_start_point = frame_index

        if not candidate_frame.occupied:
            LoggingSystem.log(f"✅ Frame {frame_index} available. Performing allocation")
            candidate_frame.occupied = True
            page.frame_number = frame_index
            page.last_access_timestamp = current_cycle
            page.present_in_main_memory = True
            return True
        LoggingSystem.log(f"❌ Frame {frame_index} not available.")

        while frame_index != search_start_point:
            frame_index, candidate_frame = self.get_next_frame()
            if not candidate_frame.occupied:
                LoggingSystem.log(f"✅ Frame {frame_index} available. Performing allocation")
                candidate_frame.occupied = True
                page.frame_number = frame_index
                page.last_access_timestamp = current_cycle
                page.present_in_main_memory = True
                return True
            LoggingSystem.log(f"❌ Frame {frame_index} not available.")
        LoggingSystem.log("⚠️ No available frame found in main memory.")
        return False

    def free_frames(self, page: PageUnit):
        target_frame = self.frame_structure[page.frame_number]
        target_frame.occupied = False
        for position in range(len(target_frame.data)):
            target_frame.data[position] = 0
        return

    def get_next_frame(self):
        current_frame = self.frame_structure[self.next_available_index]
        current_index = self.next_available_index
        self.next_available_index = (self.next_available_index + 1) % len(self.frame_structure)
        return current_index, current_frame

    def check_availability(self, required_page_count):
        free_counter = 0
        for frame in self.frame_structure:
            if not frame.occupied:
                free_counter += 1
                if free_counter == required_page_count:
                    return True
        return False

    def count_occupied_frames(self):
        counter = 0
        for frame in self.frame_structure:
            if frame.occupied:
                counter += 1
        return counter

    def get_total_frames(self):
        return len(self.frame_structure)


class SecondaryStorage:
    def __init__(self, total_storage_size, page_size):
        self.total_frame_capacity = ceil(total_storage_size / page_size)
        self.virtual_repository = []

    def store_page(self, page: PageUnit, frame: MemoryElement):
        if len(self.virtual_repository) >= self.total_frame_capacity:
            print("⚠️ Maximum capacity of secondary storage reached!")
            return

        self.virtual_repository.append(_VirtualStorageUnit(frame, page))
        print(f"💾 Page {page.page_id} of process P{page.process_id} was transferred to secondary storage")

    def recover_page(self, requested_page):
        for index in range(len(self.virtual_repository)):
            stored_page = self.virtual_repository[index].reference_page
            if (stored_page.page_id == requested_page.page_id and 
                stored_page.process_id == requested_page.process_id):
                recovered_unit = self.virtual_repository.pop(index)
                return recovered_unit.preserved_data
        print(f"🔍 Page {requested_page.page_id} of process P{requested_page.process_id} not found in secondary storage")
        return None

    def count_used_frames(self):
        return len(self.virtual_repository)


class _VirtualStorageUnit:
    def __init__(self, frame: MemoryElement, page: PageUnit):
        self.preserved_data = self._preserve_frame_content(frame)
        self.reference_page = page

    def _preserve_frame_content(self, frame):
        preserved_data = []
        if frame is not None:
            for position in range(frame.size):
                if frame.data[position] != 0:
                    preserved_data.append((position, frame.data[position]))
        return preserved_data 