import m5
from m5.objects import Cache


class L1Cache(Cache):
    assoc = 4
    tag_latency = 2
    data_latency = 2
    response_latency = 2
    mshrs = 4
    tgts_per_mshr = 20

    def _init_(self, options=None):
        super(L1Cache, self)._init_()
        
    def connectCPU(self, cpu):
        '''# need to define this in a base class!'''
        # define in subclass
        raise NotImplementedError

    def connectBus(self, bus):
        '''connect this cache to a memory-side bus'''
        self.mem_side = bus.cpu_side_ports

class L1ICache(L1Cache):
    size = '32kB'

    def _init_(self, opts=None):
        super(L1ICache, self)._init_(opts)
        if not opts or not opts.l1i_size:
            return
        print(f"L1I size={opts.l1i_size}")
        self.size = opts.l1i_size

    def connectCPU(self, cpu):
        '''connect this cache to a CPU icache port'''
        self.cpu_side = cpu.icache_port

class L1DCache(L1Cache):
    size = '32kB'

    def _init_(self, opts=None):
        super(L1DCache, self)._init_(opts)
        if not opts or not opts.l1d_size:
            return
        print(f"L1D size={opts.l1d_size}")
        self.size = opts.l1d_size

    def connectCPU(self, cpu):
        '''connect this cache to a CPU dcache port'''
        self.cpu_side = cpu.dcache_port

class L2Cache(Cache):
    size = '512kB'
    assoc = 16
    tag_latency = 20
    data_latency = 20
    response_latency = 20
    mshrs = 20
    tgts_per_mshr = 12

    def _init_(self, opts=None):
        super(L2Cache, self)._init_()
        if not opts or not opts.l2_size:
            return
        print(f"L2 size={opts.l2_size}")
        self.size = opts.l2_size
        

    def connectCPUSideBus(self, bus):
        '''connect L2 cache to mem size '''
        self.cpu_side = bus.mem_side_ports

    def connectMemSideBus(self, bus):
        self.mem_side = bus.cpu_side_ports