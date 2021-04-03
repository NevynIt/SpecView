import numpy as np
import enum



class Block:
    class Domains(enum.Enum):
        NONE = 0
        TIME = 1
        FREQUENCY = 2
        TONE = 3

    def __init__(self):
        self.domain = Block.Domains(Block.Domains.NONE)
        self.EOF = False
        self.resolution = np.zeros( (2,) )
        self.bounds = np.zeros( (2,2) )
        self.data = np.zeros( (0,0,0) )