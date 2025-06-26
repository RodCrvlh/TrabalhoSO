from enum import Enum
from math import ceil
from typing import List
from paging_system import ProcessPageCollection


class ProcessState(Enum):
    INITIALIZED = 0
    WAITING = 1
    BLOCKED = 2
    RUNNING = 3
    TERMINATED = 4
    WAITING_SUSPENDED = 5
    BLOCKED_SUSPENDED = 6


class ProcessEntity:
    def __init__(self, process_id: int, total_size: int, page_size):
        self.id = process_id
        self.total_size = total_size
        self.page_size = page_size
        self.current_state = ProcessState.INITIALIZED
        self.operation_history: List[str] = []
        self.page_manager = ProcessPageCollection()
        self.page_manager.initialize_pages(total_size, page_size, process_id)

    def terminate_process(self):
        self.current_state = ProcessState.TERMINATED
        self.total_size = 0

    def get_pages(self):
        return self.page_manager.page_set

    def calculate_page_and_offset(self, logical_address):
        page_number = logical_address // self.page_size
        offset = logical_address % self.page_size
        if not self.validate_address(logical_address):
            pass
        return {"page": page_number, "offset": offset}

    def validate_address(self, logical_address):
        if logical_address < 0:
            raise Exception("⚠️ Critical error: Negative address value is not allowed.")

        page_count = ceil(self.total_size / self.page_size)
        corresponding_page = logical_address // self.page_size
        corresponding_offset = logical_address % self.page_size
        last_valid_page = page_count - 1

        if corresponding_page > last_valid_page:
            raise Exception(f"⚠️ Memory violation detected: Attempt to access non-existent page.\n"
                            f"📍 Requested page: {corresponding_page} | Offset: {corresponding_offset} | Address: {logical_address}")

        unused_space = (page_count * self.page_size) - self.total_size
        max_valid_offset = self.page_size - unused_space - 1
        if corresponding_page == last_valid_page and corresponding_offset > max_valid_offset:
            raise Exception("⚠️ Invalid access: Attempt to access unallocated region of last page.\n"
                            f"📍 Page: {corresponding_page} | Offset: {corresponding_offset} | Address: {logical_address}")
        return True


class ProcessRegistry:
    def __init__(self, page_size):
        self.page_size = page_size
        self.next_available_id = 0
        self.active_processes: List[ProcessEntity] = []
        self.terminated_processes: List[ProcessEntity] = []
        self.ids_in_use = set()

    def create_new_process(self, process_size, custom_id=None):
        final_id = self.generate_id(custom_id)
        self.active_processes.append(ProcessEntity(final_id, process_size, self.page_size))
        return final_id

    def generate_id(self, custom_id):
        if custom_id and custom_id in self.ids_in_use:
            raise Exception("⚠️ ID conflict: The specified ID is already in use. Consider using an automatic ID.")
        elif custom_id:
            self.ids_in_use.add(custom_id)
            return custom_id

        candidate_id = self.next_available_id
        while candidate_id in self.ids_in_use:
            candidate_id = self.next_available_id
            self.next_available_id += 1
        self.ids_in_use.add(candidate_id)
        return candidate_id

    def get_active_processes(self):
        return self.active_processes

    def find_process(self, process_id):
        if process_id is None:
            return None
        for process in self.active_processes:
            if process.id == process_id:
                return process

    def get_process_index(self, process_id):
        for index, process in enumerate(self.active_processes):
            if process.id == process_id:
                return index

    def terminate_process(self, process):
        self.active_processes.remove(process)
        self.terminated_processes.append(process) 