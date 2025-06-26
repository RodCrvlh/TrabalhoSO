from logging_system import LoggingSystem
from management_core import ManagementCore
from command_processor import CommandProcessor


def get_input_with_default(prompt, default_value, conversion_type=int):
    """Requests user input with default value"""
    input_value = input(f"{prompt} (default: {default_value}): ").strip()
    if input_value == "":
        return default_value
    try:
        return conversion_type(input_value)
    except ValueError:
        print(f"⚠️ Invalid value. Using default: {default_value}")
        return default_value


def configure_system():
    """Configures system parameters with original default values"""
    print("🏗️ Virtual Memory System Configuration")
    print("📋 Press Enter to use the original system default values\n")
    
    # Original default values
    MB = pow(2, 20)
    TB = pow(2, 40)
    
    # Collect user configurations
    page_size = get_input_with_default(
        "Enter the frame/page size (bytes)", 
        1 * MB
    )
    
    address_bits = get_input_with_default(
        "Enter the logical address size in bits", 
        64
    )
    
    tlb_entries = get_input_with_default(
        "Enter the number of TLB entries", 
        16  # Reasonable default value for TLB (new feature)
    )
    
    main_memory_size = get_input_with_default(
        "Enter the main memory size (bytes)", 
        1 * MB
    )
    
    secondary_memory_size = get_input_with_default(
        "Enter the secondary memory size (bytes)", 
        1 * TB
    )
    
    return {
        'page_size': page_size,
        'address_bits': address_bits,
        'tlb_entries': tlb_entries,
        'main_memory_size': main_memory_size,
        'secondary_memory_size': secondary_memory_size
    }


def run_system():
    # Get user configurations
    config = configure_system()
    
    print(f"\n💾 System configurations:")
    print(f"📄 Page size: {config['page_size']} bytes")
    print(f"🧠 Main memory: {config['main_memory_size']} bytes")
    print(f"💿 Secondary memory: {config['secondary_memory_size']} bytes")
    print(f"🔢 Address bits: {config['address_bits']} bits")
    print(f"⚡ TLB entries: {config['tlb_entries']}")
    
    print("\n⏳ Initializing virtual memory system...")
    print("📋 This operation may take a few moments to complete")
    
    if config['main_memory_size'] % config['page_size'] != 0:
        raise Exception("⚠️ Configuration error: Memory size is not a multiple of page size.")
    
    # Create system core with configurations
    system_core = ManagementCore(
        config['main_memory_size'], 
        config['page_size'],
        config['secondary_memory_size']
    )
    
    processor = CommandProcessor(system_core)
    processor.execute_instruction_file("./instructions.txt")
    
    input("\n🎉 System completed successfully! Press any key to exit...")


LoggingSystem.enable_debug()
run_system() 