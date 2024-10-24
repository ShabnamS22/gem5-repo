import argparse
import os
import sys
import m5
from m5.objects import *
from m5.params import NULL
from m5.util import addToPath, fatal, warn

# Add gem5 configs path
addToPath("/home/shivay/gem5/configs")

from common import CacheConfig, CpuConfig, MemConfig, Options, Simulation
from example.Caches import L1_ICache, L1_DCache, L2Cache
from common.FileSystemConfig import config_filesystem

# Default cache parameters (can be changed later for experimentation)
DEFAULT_L1I_SIZE = '32kB'
DEFAULT_L1D_SIZE = '32kB'
DEFAULT_L2_SIZE = '1MB'
DEFAULT_ASSOC = 2
DEFAULT_BLOCK_SIZE = 64

def configure_caches(args, system):
    """ Configure the caches with default or user-specified parameters """

    # L1 Instruction and Data Cache
    for cpu in system.cpu:
        cpu.icache = L1_ICache(
            size=args.l1i_size if args.l1i_size else DEFAULT_L1I_SIZE,
            assoc=args.l1i_assoc if args.l1i_assoc else DEFAULT_ASSOC,
            block_size=args.block_size if args.block_size else DEFAULT_BLOCK_SIZE,
        )
        cpu.dcache = L1_DCache(
            size=args.l1d_size if args.l1d_size else DEFAULT_L1D_SIZE,
            assoc=args.l1d_assoc if args.l1d_assoc else DEFAULT_ASSOC,
            block_size=args.block_size if args.block_size else DEFAULT_BLOCK_SIZE,
        )

        # Connect L1 cache ports to CPU
        cpu.icache.cpu_side = cpu.icache_port
        cpu.dcache.cpu_side = cpu.dcache_port

        # L2 Cache
        system.l2 = L2Cache(
            size=args.l2_size if args.l2_size else DEFAULT_L2_SIZE,
            assoc=args.l2_assoc if args.l2_assoc else DEFAULT_ASSOC,
            block_size=args.block_size if args.block_size else DEFAULT_BLOCK_SIZE,
        )
        
        # Connect L2 cache
        system.l2.cpu_side = cpu.icache.mem_side
        system.l2.mem_side = cpu.dcache.mem_side

    return system

def get_processes(args):
    """ Set up the workload processes """

    workloads = args.cmd.split(';')
    processes = []

    for idx, workload in enumerate(workloads):
        process = Process(pid=100 + idx)
        process.executable = workload
        process.cmd = [workload] + args.options.split() if args.options else [workload]
        processes.append(process)

    return processes

# Set up argument parsing
parser = argparse.ArgumentParser(description="Run gem5 cache simulation")
Options.addCommonOptions(parser)
Options.addSEOptions(parser)

# Add cache-related arguments
parser.add_argument('--l1i_size', type=str, help='L1 instruction cache size')
parser.add_argument('--l1d_size', type=str, help='L1 data cache size')
parser.add_argument('--l2_size', type=str, help='L2 cache size')
parser.add_argument('--l1i_assoc', type=int, help='L1 instruction cache associativity')
parser.add_argument('--l1d_assoc', type=int, help='L1 data cache associativity')
parser.add_argument('--l2_assoc', type=int, help='L2 cache associativity')
parser.add_argument('--block_size', type=int, help='Cache block size (bytes)')

args = parser.parse_args()

# Create the system and CPU configuration
(CPUClass, test_mem_mode, FutureClass) = Simulation.setCPUClass(args)
system = System(
    cpu=[CPUClass(cpu_id=i) for i in range(args.num_cpus)],
    mem_mode=test_mem_mode,
    mem_ranges=[AddrRange(args.mem_size)],
)

# Configure caches
system = configure_caches(args, system)


# Set up the process workloads
processes = get_processes(args)
for i, cpu in enumerate(system.cpu):
    cpu.workload = processes[i]
    cpu.createThreads()

# Configure memory
MemConfig.config_mem(args, system)

# System parameters
system.voltage_domain = VoltageDomain(voltage=args.sys_voltage)
system.clk_domain = SrcClockDomain(clock=args.sys_clock, voltage_domain=system.voltage_domain)

root = Root(full_system=False, system=system)

# Run the simulation
Simulation.run(args, root, system)
