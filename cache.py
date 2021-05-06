import math
from queue import PriorityQueue

hex_to_bin = {
    "0" : "0000",
    "1" : "0001",
    "2" : "0010",
    "3" : "0011",
    "4" : "0100",
    "5" : "0101",
    "6" : "0110",
    "7" : "0111",
    "8" : "1000",
    "9" : "1001",
    "a" : "1010",
    "b" : "1011",
    "c" : "1100",
    "d" : "1101",
    "e" : "1110",
    "f" : "1111"
}


def bin_to_dec(b):
    ans = 0
    for c in b:
        if c == '0':
            ans *= 2
        elif c == '1':
            ans = ans*2 + 1
    return ans


class Block:
    def __init__(self, rem, B):
        self.rem = rem
        self.data = ['00']*B

class Set:
    def __init__(self, i, A, B):
        self.B = B
        self.index = i
        self.A = A
        self.t = 1
        self.blocks = []


    def add_block(self, blk):
        if len(self.blocks) <  self.A:
            # add the block in empty slot
            self.blocks.append((self.t, blk))
            self.t += 1
            return None
        else:
            # replace Least Recently Used
            self.blocks.sort(reverse=True)
            kob = self.blocks[len(self.blocks)-1][1]
            self.blocks.pop()
            self.blocks.append((self.t, blk))
            self.t += 1
            return kob
    

class Set1(Set):
    def __init__(self,i,A,B):
        super().__init__(i, A, B)
    def read(self, rem):
        for pri,blk in self.blocks:
            if blk.rem == rem:
                self.blocks.remove((pri, blk))
                self.blocks.append((self.t, blk))
                self.t += 1
                return blk
        return None
    
    def write(self, rem, offset, d):
        for pri,blk in self.blocks:
            if blk.rem == rem:
                self.blocks.remove((pri, blk))
                blk.data[offset] = d
                self.blocks.append((self.t, blk))
                self.t += 1
                return True
        return False


class Set2(Set):
    def __init__(self,i,A,B):
        super().__init__(i, A, B)
    def read(self, rem):
        for pri,blk in self.blocks:
            if blk.rem == rem:
                self.blocks.remove((pri, blk))
                return blk
        return None

    def write(self, rem, offset, d):
        for pri,blk in self.blocks:
            if blk.rem == rem:
                self.blocks.remove((pri, blk))
                blk.data[offset] = d
                return blk
        return None


class Cache:
    def __init__(self, A, B, C):
           self.A = A
           self.B = B
           self.C = C
           self.n_blocks = C/B
           self.n_sets = self.n_blocks / A
           self.sets = []
           self.indxs = int(math.log2(self.n_sets))
    
    def add_block(self, blk):
        rem = blk.rem
        set_indx = bin_to_dec(rem[len(rem)-self.indxs:])
        s = self.sets[set_indx]
        return s.add_block(blk)

class L1Cache(Cache):
    def __init__(self, A, B, C):
            super().__init__(A, B, C)
            for i in range(int(self.n_sets)):
                self.sets.append(Set1(i, self.A, self.B))
    
    def read(self, rem):
            # tag = rem[:len(rem)-indxs]
            set_indx = bin_to_dec(rem[len(rem)-self.indxs:])
            s = self.sets[set_indx]
            return s.read(rem)

    def write(self, rem, offset, d):
            set_indx = bin_to_dec(rem[len(rem)-self.indxs:])
            s = self.sets[set_indx]
            return s.write(rem, offset, d)

    

class L2Cache(Cache):
    def __init__(self, A, B, C):
            super().__init__(A,B,C)
            for i in range(int(self.n_sets)):
               self.sets.append(Set2(i, self.A, self.B))
    

    def read(self, rem):
            # tag = rem[:len(rem)-indxs]
            set_indx = bin_to_dec(rem[len(rem)-self.indxs:])
            s = self.sets[set_indx]
            return s.read(rem)

    def write(self, rem, offset, d):
            set_indx = bin_to_dec(rem[len(rem)-self.indxs:])
            s = self.sets[set_indx]
            return s.write(rem, offset, d)
    

class Cache_Controller:
    def __init__(self,A1,C1,A2,C2,B,p):
        self.L1 = L1Cache(A1,B,C1)
        self.L2 = L2Cache(A2,B,C2)
        self.B = B
        self.MEM = ["00"] * (2**12)
        self.offs = int(math.log(self.B,2))

        self.L1l = 1
        self.L2l = 1
        self.MEMl = 1

        self.processor = p

    
    def read(self, addr):
        print("addr : ", addr)
        bin_add  = ""
        for i in range(2,10):
            bin_add += hex_to_bin[addr[i]]
        
        rem = bin_add[ : 32-self.offs]
        offset = bin_to_dec( bin_add[32-self.offs : ])

        res = self.L1.read(rem)

        self.processor.total_clock_cycles += self.L1l
        self.processor.total_stalls += self.L1l

        if res != None:
            print("found in L1")
            return res.data[offset]

        res = self.L2.read(rem)

        self.processor.total_clock_cycles += self.L2l
        self.processor.total_stalls += self.L2l

        if res != None:
            self.add_to_L1(res)
            return res.data[offset]

        self.processor.total_clock_cycles += self.MEMl
        self.processor.total_stalls += self.MEMl

        new_blk = Block(rem, self.B)
        addr = bin_to_dec(rem + '0'*self.offs)
        for i in range(self.B):
            new_blk.data[i] = self.MEM[addr + i]

        self.add_to_L1(new_blk)
        return new_blk.data[offset]
        
    
    def add_to_L1(self, b1):
        kob = self.L1.add_block(b1)
        if kob != None:
            self.add_to_L2(kob)

    def add_to_L2(self ,b2):
        kob = self.L2.add_block(b2)
        if kob != None:
            addr = bin_to_dec(kob.rem + '0'*self.offs)
            for i in range(self.B):
                self.MEM[addr + i] = kob.data[i]
    
    def write(self, addr, d):
        bin_add  = ""
        for i in range(2,10):
            bin_add += hex_to_bin[addr[i]]
        
        rem = bin_add[ : 32-self.offs]
        offset = bin_to_dec( bin_add[32-self.offs : ])

        ok = self.L1.write(rem,offset,d)
        # updates the value and priority
        if not ok:
            kob = self.L2.write(rem, offset,d)
            # updates the value and extracts
            if kob != None:
                self.add_to_L1(kob)
            else:

                new_blk = Block(rem, self.B)
                addr = bin_to_dec(rem + '0'*self.offs)
                self.MEM[addr + offset] = d
                for i in range(self.B):
                    new_blk.data[i] = self.MEM[addr + i]

                self.add_to_L1(new_blk)
    
    def clear(self):
        self.L1 = L1Cache(self.L1.A, self.L1.B, self.L1.C)
        self.L2 = L2Cache(self.L2.A, self.L2.B, self.L2.C)
        self.MEM = ["00"] * (2**12)








def display(c):
    print("L1 : \n")
    for s in c.L1.sets:
        print("set : ", s.index)
        for p,b in s.blocks:
            for d in b.data:
                print(d, end=" ")
            print()
        print("\n")

    print("---------------------")
    print("L2 : \n")
    for s in c.L2.sets:
        print("set : ", s.index)
        for p,b in s.blocks:
            for d in b.data:
                print(d, end=" ")
            print()
        print("\n")
    
    print("---------------------------------------------------------------------")






def test1():
    c = Cache_Controller(2,32,2,32,4)


    c.write("0x00000001", "10")
    display(c)
    c.write("0x00000011", "20")
    display(c)
    c.write("0x00000021", "30")
    display(c)
    c.write("0x00000031", "40")
    display(c)
    c.write("0x00000041", "50")
    display(c)
    c.write("0x00000051", "60")
    display(c)
    c.write("0x00000002", "70")
    display(c)

    c.write("0x00000004", "72")
    display(c)

