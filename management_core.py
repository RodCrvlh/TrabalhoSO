from math import ceil
from typing import List
from random import randint

from process_entity import ProcessEntity
from logging_system import LoggingSystem
from memory_subsystem import MainMemoryManager, SecondaryStorage
from paging_system import PageUnit
from process_entity import ProcessRegistry


class ManagementCore:

    def __init__(self, main_memory_size, page_size, secondary_memory_size):
        self.page_size = page_size
        self.main_memory_size = main_memory_size
        self.secondary_memory_size = secondary_memory_size
        LoggingSystem.log("🚀 Initializing process registry system")
        self.process_registry = ProcessRegistry(page_size)
        LoggingSystem.log("🏗️ Setting up main memory subsystem")
        self.main_memory = MainMemoryManager(main_memory_size, page_size)
        LoggingSystem.log("✅ Main memory subsystem configured successfully\n")
        self.secondary_storage = SecondaryStorage(secondary_memory_size, page_size)
        LoggingSystem.log("✅ Secondary storage subsystem configured successfully\n")

    def check_available_space(self, requested_size: int):
        free_main_space = self.calculate_free_main_space()
        free_secondary_space = (self.secondary_storage.total_frame_capacity -
                              self.secondary_storage.count_used_frames()) * self.page_size
        return (free_secondary_space + free_main_space) >= requested_size

    def create_process(self, requested_size, current_cycle, process_id=None):
        LoggingSystem.log(f"🔄 Starting process creation with {requested_size} bytes")
        sufficient_space = self.check_available_space(requested_size)
        if sufficient_space:
            LoggingSystem.log(f"✅ Sufficient resources identified in memory system\n")
            final_id = self.process_registry.create_new_process(requested_size, process_id)
            LoggingSystem.log(
                f"📋 Process P{final_id} registered at index {self.process_registry.get_process_index(final_id)}\n")
            process = self.process_registry.find_process(final_id)
            LoggingSystem.log(f"🔍 Checking availability of {requested_size} bytes in main memory")
            LoggingSystem.log(f"📦 Allocating pages in memory system")
            self.allocate_process_pages(process.get_pages(), current_cycle)
            LoggingSystem.log(
                f"🎉 Process allocated successfully in system\n"
                f"📊 Main memory utilization: {self.calculate_main_usage_percentage() * 100:.2f}%\n"
                f"📊 Secondary storage utilization: {self.calculate_secondary_usage_percentage() * 100:.2f}%\n")
            return
        LoggingSystem.log(f"❌ Insufficient space in system. Allocation cancelled")

    def calculate_secondary_usage_percentage(self):
        return self.secondary_storage.count_used_frames() / self.secondary_storage.total_frame_capacity
    
    def calculate_main_usage_percentage(self):
        return self.main_memory.count_occupied_frames() / self.main_memory.get_total_frames()

    def calculate_page_count(self, size):
        return ceil(size / self.page_size)

    def allocate_process_pages(self, page_set: List[PageUnit], current_cycle):
        for index, page in enumerate(page_set):
            if not page.present_in_main_memory:
                LoggingSystem.log(f"📄 Page {index} absent from main memory.")
                if self.main_memory.count_occupied_frames() < self.main_memory.get_total_frames():
                    self.main_memory.allocate_space(page, current_cycle)
                else:
                    self.secondary_storage.store_page(page, None)
                LoggingSystem.log(f"✅ Page {index} allocated successfully\n")
            else:
                LoggingSystem.log(f"✅ Page {index} already present in main memory. Continuing")

    def calculate_free_main_space(self):
        return (self.main_memory.get_total_frames() - self.main_memory.count_occupied_frames()) * self.page_size

    def calculate_secondary_usage_bytes(self):
        return self.secondary_storage.count_used_frames() * self.page_size

    def execute_memory_read(self, process_id, logical_address, current_cycle):
        process = self.process_registry.find_process(process_id)

        page_info = process.calculate_page_and_offset(logical_address)

        print(f"📖 Executing read on page {page_info['page']}, offset {page_info['offset']} of process P{process_id}")
        requested_page = process.get_pages()[page_info['page']]
        if not requested_page.present_in_main_memory:
            self.apply_lru_algorithm(requested_page, current_cycle)
        target_frame = self.main_memory.frame_structure[requested_page.frame_number]
        print(
            f"📊 Value found at offset {page_info['offset']} of frame {requested_page.frame_number}: {target_frame.data[page_info['offset']]}")
        requested_page.last_access_timestamp = current_cycle
        return

    def execute_memory_write(self, process_id, logical_address, value, current_cycle):
        process = self.process_registry.find_process(process_id)

        page_info = process.calculate_page_and_offset(logical_address)

        print(f"✏️ Executing write on page {page_info['page']}, offset {page_info['offset']} of process P{process_id}")
        requested_page = process.get_pages()[page_info['page']]
        if not requested_page.present_in_main_memory:
            self.apply_lru_algorithm(requested_page, current_cycle)
        target_frame = self.main_memory.frame_structure[requested_page.frame_number]
        target_frame.data[page_info["offset"]] = value
        requested_page.modified = True
        print(f"💾 Value {value} written to offset {page_info['offset']} of frame {requested_page.frame_number}")
        requested_page.last_access_timestamp = current_cycle
        return

    def execute_instruction(self, process_id, logical_address, current_cycle):
        process = self.process_registry.find_process(process_id)

        page_info = process.calculate_page_and_offset(logical_address)

        print(
            f"⚡ Executing instruction on page {page_info['page']}, offset {page_info['offset']} of process P{process_id}")
        requested_page = process.get_pages()[page_info['page']]
        if not requested_page.present_in_main_memory:
            self.apply_lru_algorithm(requested_page, current_cycle)
        computation_result = randint(0, 10000)
        operation_type = "addition" if logical_address % 2 == 0 else "subtraction"
        print(
            f"🧮 Result of {operation_type} on page {page_info['page']}, offset {page_info['offset']} of process P{process_id}: {computation_result}")
        requested_page.last_access_timestamp = current_cycle
        return

    def access_io_device(self, process_id, device_id):
        print(f"🔌 Process P{process_id} is performing I/O operation on device {device_id}")

    def apply_lru_algorithm(self, requested_page: PageUnit, current_cycle):
        least_recent_page = self.process_registry.get_active_processes()[0].get_pages()[0]
        for process in self.process_registry.get_active_processes():
            for page in process.get_pages():
                if not least_recent_page.present_in_main_memory:
                    least_recent_page = page
                elif page.present_in_main_memory and page.last_access_timestamp < least_recent_page.last_access_timestamp:
                    least_recent_page = page
        print(
            f"🔄 Applying LRU algorithm: Replacing page from frame {least_recent_page.frame_number} (P{least_recent_page.process_id}) with page {requested_page.page_id} (P{requested_page.process_id})")

        least_recent_page.present_in_main_memory = False
        self.secondary_storage.store_page(least_recent_page,
                                             self.main_memory.frame_structure[least_recent_page.frame_number])
        self.main_memory.free_frames(least_recent_page)
        least_recent_page.frame_number = None
        least_recent_page.last_access_timestamp = None
        
        recovered_content = self.secondary_storage.recover_page(requested_page)
        self.main_memory.allocate_space(requested_page, current_cycle)

        if recovered_content is not None and len(recovered_content) > 0:
            destination_frame = self.main_memory.frame_structure[requested_page.frame_number]
            while len(recovered_content) > 0:
                item = recovered_content.pop()
                destination_frame.data[item[0]] = item[1]
        return

    def terminate_process(self, process_id, current_cycle):
        print(f"🔚 Starting termination of process P{process_id}\n⏳ This operation may take a few moments...")
        process = self.process_registry.find_process(process_id)
        for i in range(len(process.get_pages())):
            page = process.get_pages()[0]
            self.deallocate_page(page, process)
        process.terminate_process()
        self.process_registry.terminate_process(process)

    def deallocate_page(self, page: PageUnit, process: ProcessEntity):
        if page.present_in_main_memory:
            self.main_memory.free_frames(page)
        else:
            self.secondary_storage.recover_page(page)
        process.page_manager.remove_page(page) 