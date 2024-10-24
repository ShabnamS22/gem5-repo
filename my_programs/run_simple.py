import sys
import os
import m5
from m5.objects import *

# Explicitly append path to 'common' directory where caches.py resids 
sys.path.append('/home/shivay/gem5/configs/common/Caches')
sys.path.append('/home/shivay/gem5/configs/example/x86')

# Import module diectly
Caches = __import__('Caches')
#print python search path to debug
print("Python search paths:")
for p in sys.path:
	print(p)

# Add the gem5 directory to path
#addToPath('../../configs/common/')
#addToPath('../configs/example/x86/')

# Import necessary configuration files from gem5
#from Caches import *
FSConfig = __import__('FSConfig')

def run_simulation():
	# Create a system
	system = System()
	system.clk_domain = SrcClockDomain()
	system.clk_domain.clock = '1GHz'
	system.clk_domain.voltage_domain = VoltageeDomain()

	# Use x86 architecture
	system.mem_mode - 'timing' 
	system.mem_ranges = [AddrRange('512MB')]

	# Create a simple CPU for the x86 architecture
	system.cpu = X86TimingSimpleCPU()

	# Create default cache configuration (L1, L2)
	system.cpu.icache = L1ICache(size='32KB')
	system.cpu.dcache = L1DCache(size='32KB')

	# Connect L1 cache to the CPU
	system.cpu.icache.connectCPU(system.cpu)
	system.cpu.dcache.connectCPU(system.cpu)

	# Create an L2 cache and connect L1 to L2
	system.l2cache = L2Cache(size='256KB')
	system.cpu.icache.connectBus(system.l2cache.cpu_side)
	system.cpu.dcache.connectBus(system.l2cache.cpu_side)

	# Create a memory bus and connect L2 to the memory bus
	system.membus = SystemXBar()
	system.l2cache.connectMemSide(system.membus)

	# Connect the CPU to the memory bus
	system.cpu.createInterruptController()
	system.system_port = system.membus.slave

	# Create DDR3 memory and connect to the memory bus
	system.mem_ctrl = DDR3_1600_8x8()
	system.mem_ctrl.range = system.mem_ranges[0]
	system.mem_ctrl.port = system.membus.master

	# Create a process to simulate a workload
	process = Process()
	process.cmd = ['/bin/ls']
	system.cpu.workload = process
	system.cpu.createThreads()

	# Instantiate the system and runt the simulation
	root = Root(full_system=False, system=system)
	m5.instantiate()

	print("Beginning simulation with defalt cache configuration")
	exit_event = m5.simulate()

	print(f"Simulation ended at tick {m5.curTick()}")
	print(f"Exit cause: {exit_event.getCause()}")

	# Access and print stats for performance analysis
	stats = m5.stats.dump()
	print(stats)

if __name__ == "__main__":
	run_simulation()
#set the command line arguments for this simulation
parser = argparse.ArgumentParser(description="Run a simple simulation")
parser.add_argument('binary', type=str, help='path to the binary to run')
args = parser.parse_args()

#create the system object
system = System()

#ste the system clock frequency
system.clk_domain = SrcClockDomain(clock='1GHz', voltage_domain=VoltageDomain())

#create CPU
system.cpu = TimingSimpleCPU()

#create the memory controller
system.membus = SystemXBar()

#create the L1 instruction cache
system.l1i_cache = L1ICache(size='32KB', assoc=2)
system.l1i_cache.connectMemSide(system.membus.mem_side_ports)

#create the L1 Data cache
system.l1d_cache = L1DCache(size='32KB', assoc=2)
system.l1d_cache.connectMemSide(system.membus.mem_side_ports)

#create the L2 cache
system.l2_cache = L2Cache(size='256KB', assoc=2)
system.l2_cache.connectMemSide(system.membus_side_ports)

#connect the l1 cache to cpu
system.cpu.icache_port = system.l1i_cache.cpu_side
system.cpu.dcache_port = system.l1d_cache.cpu_side

#connect the cpu to the memory bus
system.l1i_cache.connectCPUSide(system.cpu.icache_port)
system.l1d_cache.connectCPUSide(system.cpu.dcache_port)

#create the main memory
system.mem_ranges = [AddrRange('512MB')]
system.mem = SimpleMemory(range=system.mem_ranges[0])

#connect memory to the memory bus
system.membus.mem_side_ports = system.mem.getPorts()

#set the binary to run
process = Process(pid=1234, exe=args[1])
system.cpu.workload = process
system.cpu.createThreads()

#set the root of the system
root = Root(full_system=False, system=system)

#initiate the simulation
m5.instantiate()

#run the simulation
print("Running the Simulation")
exit_event = m5.simulate()
print("Exiting @ tick %i because %s" % (m5.curTick(), exit_event.getCause()))

#output simulation statistics
print("Cache hit rate: %s" % system.l1i_cache.hitRate())
print("L1 Cache Miss Rate: %s" % system.l1i_cache.missRate())
print("Average memory access latency: %s" % system.membus.getAverageLatency())
