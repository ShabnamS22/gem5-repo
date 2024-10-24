import os
import m5
from m5.objects import *

#create root systm
#root = Root(full_system=False)

#create the system we are going to simulate
system = System()

#set the clock frequency of the system(and all of its children)
system.clk_domain = SrcClockDomain(clock='1GHz', voltage_domain=VoltageDomain())
#system.clk_domain.clock = '1GHZ'
#system.clk_domain.voltage_domain = VoltageDomain()

#set up the system
system.mem_mode = "timing"
system.mem_ranges = [AddrRange("512MB")]

#Create simple CPU
system.cpu = X86TimingSimpleCPU()

#Create a memory bus, a system crossbar, in this case
system.membus = SystemXBar()

#Hook CPU ports to membus
system.cpu.icache_port = system.membus.cpu_side_ports
system.cpu.dcache_port = system.membus.cpu_side_ports

#create interrupt controller from CPU and connect to membus
system.cpu.createInterruptController()

#Connect interrupt care to memory
system.cpu.interrupts[0].pio = system.membus.mem_side_ports
system.cpu.interrupts[0].int_requestor = system.membus.cpu_side_ports
system.cpu.interrupts[0].int_responder = system.membus.mem_side_ports

#create DDR3 memory controller and connect to membus
system.mem_ctrl = MemCtrl()
system.mem_ctrl.dram = DDR3_1600_8x8()
system.mem_ctrl.dram.range = system.mem_ranges[0]
system.mem_ctrl.port = system.membus.mem_side_ports

#connect the system up to the membus
system.system_port = system.membus.cpu_side_ports

#create path
binary = '/home/shivay/gem5/my_programs/hello'

system.workload = SEWorkload.init_compatible(binary)

#create process for sample Hello World application
process = Process()
#set command cmd to begin executable
process.cmd = [binary]
#set cpu to use process as its workload and create thread context
system.cpu.workload = process
system.cpu.createThreads()

#setup root
root = Root(full_system=False, system=system)
m5.instantiate()
print("Beginning simulation!")
exit_event = m5.simulate()
print("Exiting @ tick {} because {}".format(m5.curTick(), exit_event.getCause()))

