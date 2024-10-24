import m5
from m5.objects import *
from caches import *

import argparse

# Argument parsing for binary and cache sizes
parser = argparse.ArgumentParser(description='A simple system with 2-level cache.')
parser.add_argument("binary", default="tests/test-progs/hello/bin/x86/linux/hello", nargs="?", type=str,
                    help="Path to the binary to execute.")
parser.add_argument("--l1i_size", default="16kB",
                    help="L1 instruction cache size. Default: 16kB.")
parser.add_argument("--l1d_size", default="64kB",
                    help="L1 data cache size. Default: 64kB.")
parser.add_argument("--l2_size", default="256kB",
                    help="L2 cache size. Default: 256kB.")

options = parser.parse_args()

# Create the system object (the parent of all objects)
system = System()

# Create system clock
system.clk_domain = SrcClockDomain()
system.clk_domain.clock = '1GHz'
system.clk_domain.voltage_domain = VoltageDomain()

# Specify memory system
system.mem_mode = 'timing'
system.mem_ranges = [AddrRange('512MB')]

# Specify the CPU
system.cpu = X86TimingSimpleCPU()

# Create L1 caches with sizes from options
system.cache_line_size = 128
system.cpu.icache = L1ICache(size=options.l1i_size)
system.cpu.dcache = L1DCache(size=options.l1d_size)

# Connect I & D caches to the CPU
system.cpu.icache.connectCPU(system.cpu)
system.cpu.dcache.connectCPU(system.cpu)

# Specify L2 bus to connect to I & D caches
system.l2bus = L2XBar()

# Connect I & D caches to L2 bus
system.cpu.icache.connectBus(system.l2bus)
system.cpu.dcache.connectBus(system.l2bus)

# Create L2 cache with size from options
system.l2cache = L2Cache(size=options.l2_size)

# Connect L2 cache to the L2 bus and memory bus
system.l2cache.connectCPUSideBus(system.l2bus)
system.membus = SystemXBar()
system.l2cache.connectMemSideBus(system.membus)

# Create an I/O controller and connect it to the memory bus
system.cpu.createInterruptController()
system.cpu.interrupts[0].pio = system.membus.mem_side_ports
system.cpu.interrupts[0].int_requestor = system.membus.cpu_side_ports
system.cpu.interrupts[0].int_responder = system.membus.mem_side_ports

# Connect system port to the memory bus
system.system_port = system.membus.cpu_side_ports

# Create the memory controller and connect to the memory bus
system.mem_ctrl = MemCtrl()
system.mem_ctrl.dram = DDR3_1600_8x8()
system.mem_ctrl.dram.range = system.mem_ranges[0]
system.mem_ctrl.port = system.membus.mem_side_ports

# Create a process and connect to CPU workload
system.workload = SEWorkload.init_compatible(options.binary)

process = Process()
process.cmd = [options.binary]
system.cpu.workload = process
system.cpu.createThreads()

# Instantiate the system and begin execution
root = Root(full_system=False, system=system)
m5.instantiate()

# Begin simulation
print("Beginning simulation!")
exit_event = m5.simulate()

# Inspect the state of the system at the end of the simulation
print('Exiting @ tick {} because {}'
      .format(m5.curTick(), exit_event.getCause()))
