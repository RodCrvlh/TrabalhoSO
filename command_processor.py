from management_core import ManagementCore


class CommandProcessor:
    def __init__(self, management_core: ManagementCore):
        self.system_core = management_core
        self.cycle_counter = 0

    def execute_instruction_file(self, file_path):
        with open(file_path) as command_file:
            for line_number, command in enumerate(command_file):
                print(f"📜 Processing command {line_number + 1}: {command.strip()}")
                self.process_command(command)
                self.cycle_counter += 1

    def process_command(self, command: str):
        process_id, operation_code, parameter_3, parameter_4 = self.parse_command(command)
        print(f"🎯 Operation type identified: {operation_code}")
        
        if operation_code == "P":
            self.system_core.execute_instruction(process_id, parameter_3, self.cycle_counter)
            return
        if operation_code == "I":
            return
        if operation_code == "C":
            self.system_core.create_process(parameter_3, self.cycle_counter, process_id)
            return
        if operation_code == "R":
            self.system_core.execute_memory_read(process_id, parameter_3, self.cycle_counter)
            return
        if operation_code == "W":
            self.system_core.execute_memory_write(process_id, parameter_3, parameter_4, self.cycle_counter)
            return
        if operation_code == "T":
            self.system_core.terminate_process(process_id, self.cycle_counter)
            return

    def parse_command(self, command):
        command_elements = command.split()
        process_id = int(command_elements[0].replace("P", ""))
        operation_type = command_elements[1]

        if operation_type == "T":
            return process_id, operation_type, None, None

        if operation_type in ["P", "R", "W", "I"]:
            parameter_3 = int(command_elements[2], 2)
        else:
            parameter_3 = int(command_elements[2])

        if operation_type != "C" and operation_type != "W":
            return process_id, operation_type, parameter_3, None
        if operation_type == "C":
            return process_id, operation_type, self.convert_size(parameter_3, command_elements[3]), None
        write_parameter = int(command_elements[3], 2)
        return process_id, operation_type, parameter_3, write_parameter

    @staticmethod
    def convert_size(unit_quantity: int, unit: str):
        KB = pow(2, 10)
        MB = pow(2, 20)
        GB = pow(2, 30)
        TB = pow(2, 40)

        if unit == "B":
            return unit_quantity
        if unit == "KB":
            return unit_quantity * KB
        if unit == "MB":
            return unit_quantity * MB
        if unit == "GB":
            return unit_quantity * GB
        if unit == "TB":
            return unit_quantity * TB
        raise Exception("⚠️ Error: Unrecognized unit of measurement. Maximum supported: TB") 