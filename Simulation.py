import logging
logging.basicConfig(level = logging.INFO)

import random
import copy
import math

##################################################################################
#                                                                                #
#                                 GLOBAL VARIABLES                               #
#                                                                                #
##################################################################################

# No. of the channels in the system
N = 0

# No. of the data group members in a program
P = 0

# No. of quality requirements
K = 0

# Channel constraint for one client
U = 0

# No. of channel groups T = N/K or T = N/U
T = 0

# Length of the index
In = 0

# Percent of > 1/5 for a ISDAA run
Greater_Percent = 0

# Average number of files on each channel
AFC = 0

# Average channel wastage
ACW = 0

# Average size for multimedia files
mu = 0

# Variance among multimedia files
sig = 0


##################################################################################
#                                                                                #
#                               FILE GENERATION                                  #
#                                                                                #
##################################################################################



def newFile_Gauss():
    global mu, sig
    temp = 0
    while True:
        temp = random.gauss(mu, sig)
        if temp > 0:
            return int(temp)



##################################################################################
#                                                                                #
#                              CLASS DEFINITIONS                                 #
#                                                                                #
##################################################################################


#############################      DATA GROUP     ################################

class DataGroupItem(object):

    def __init__(self, Gindex, Dindex, length, Sindex = -1, Pieces = 1, \
                    Combined = False, ComList = None):

        global In

        # Dindex: -1 hole
        # 1,2... data
        self.data_index = Dindex

        # Sindex: -1 only one piece
        # -2 index
        # 0,1,2... more than one pieces
        self.data_second_index = Sindex

        self.data_indexed_length = length
        if Combined:
            temp = 0
            for x in ComList:
                temp += x.indexed_item_len()
            self.data_indexed_length = temp
        else:
            if Sindex >= 0:
                self.data_indexed_length += In

        self.data_length = length
        if Combined:
            temp = 0
            for x in ComList:
                temp += x.item_len()
            self.data_length = temp

        # Gindex: -1 hole
        # 1,2... data
        self.group_index = Gindex

        # Combined: False only one piece
        # True several pieces are combined together
        # ComList is used to pass the list where the pieces are stored
        self.combined = Combined
        self.comlist = copy.deepcopy(ComList)

        # Pieces: No. of pieces a data is divided into
        self.pieces = Pieces

    def get_pieces(self):
        return self.pieces

    def set_pieces(self, x):
        self.pieces = x

    def is_combined(self):
        return self.combined

    def get_comlist(self):
        return self.comlist

    def print_item(self):
        if not self.combined:
            print '    G%d Q%d S%d P%d: %d'%(self.group_index, self.data_index, \
                self.data_second_index, self.pieces, self.data_length)
        else:
            print '    Combined:'
            for x in range(0,len(self.comlist)):
                print '      G%d Q%d S%d P%d: %d'%(self.comlist[x].group_index, \
                    self.comlist[x].data_index, self.comlist[x].data_second_index, \
                    self.comlist[x].pieces, self.comlist[x].data_length)

    def item_len(self):
        return self.data_length

    def indexed_item_len(self):
        return self.data_indexed_length

    def set_len(self,x):
        self.data_length = x

    def set_indexed_len(self, x):
        self.data_indexed_length = x

    def get_data_index(self):
        return self.data_index

    def get_group_index(self):
        return self.group_index

    def get_data_second_index(self):
        return self.data_second_index

    def set_data_second_index(self,x):
        self.data_second_index = x

    def cut_len(self,x):
        self.data_length -= x


class DataGroupMember(object):

    def __init__(self, Gindex, subStream = None):

        global K

        self.subStream = []
        self.member_index = Gindex

        # Generate the items of a data group
        # Here using random generation-------------------------need modification
        # The range is (30,100), because of the requirement of 
        # 1/5 approximation algorithm in ISDAA
        File = newFile_Gauss()
        for j in range(1,K+1):
            self.subStream.append(DataGroupItem(self.member_index, j, \
                random.randint(30, 1000)))

    def print_member(self):
        for i in self.subStream:
            i.print_item()

    def max_len(self):
        return max(self.subStream, key = lambda x:x.indexed_item_len()).indexed_item_len()

    def total_len(self):
        temp_len = 0
        for x in self.subStream:
            temp_len += x.item_len()
        return temp_len

    def get_substream(self):
        return self.subStream

    def get_memberIndex(self):
        return self.member_index

    def add_item(self,k):
        self.subStream.append(k)

    def del_item(self,k):
        self.subStream.remove(k)

    def clear(self):
        self.subStream[:] = []


class DataGroup(object):
    
    def __init__(self, empty, G_1 = None):

        global P

        self.G_1 = []
        
        if empty == False:

            # Generate the Group of data groups
            # Here using random generation-------------------------need modification
            for i in range(1,P+1):
                self.G_1.append(DataGroupMember(i))

    def print_groups(self):
        for i in self.G_1:
            print '\nGroup %d:' %(i.get_memberIndex())
            i.print_member()

    def sort_groups(self):
        self.G_1.sort(key = lambda x:x.max_len())

    def get_member(self,a):
        return self.G_1[a]

    def add_member(self,a):
        self.G_1.append(a)

    def del_member(self,*x):
        for a in x:
            for index in range(0, len(self.G_1)):
                if self.G_1[index].get_memberIndex() == a.get_memberIndex():
                    del self.G_1[index]
                    break

    def get_G1(self):
        return self.G_1


#############################      CHANNEL GROUP     ################################

class ChannelGroupItem(object):

    def __init__(self,index,length = 0,contain = None):
        self.chan_index = index
        self.chan_length = length
        self.chan_contain = []

    def insert_data(self,k):
        self.chan_contain.append(k)
        self.chan_length += k.item_len()

    def print_item(self):
        hasHole = True
        if len(self.chan_contain) != 0:
            D = self.chan_contain[0].get_group_index()
            print '\nC%d (%d):' %(self.chan_index, self.chan_length)
            print '----------------------------------------'
            for i in self.chan_contain:
                if i.get_group_index() == -1:
                    i.print_item()
                    print '----------------------------------------'
                    hasHole = True
                elif i.get_group_index() != D:
                    if not hasHole:
                        print '----------------------------------------'
                    i.print_item()
                    hasHole = False
                    D = i.get_group_index()
                else:
                    i.print_item()
                    hasHole = False
            if not hasHole:
                print '----------------------------------------'

    def item_len(self):
        return self.chan_length

    def data_len(self):
        return sum([x.item_len() for x in self.chan_contain if x.get_data_index() > 0 \
            and x.get_data_second_index() > -2 ])

    def get_chan_contain(self):
        return self.chan_contain

    def line_access_time(self, data_group_member, level, start_time):

        contain = []
        accu_time = 0
        flag = False

        result_time = 0

        for item in self.chan_contain:
            if item.get_group_index() == data_group_member and\
                item.get_data_index() <= level:
                flag = True
                if len(contain) > 0:
                    if contain[-1][2]:
                        contain[-1][1] += item.item_len() - 1
                        accu_time += item.item_len()
                        continue
            else:
                flag = False
                if len(contain) > 0:
                    if not contain[-1][2]:
                        contain[-1][1] += item.item_len() - 1
                        accu_time += item.item_len()
                        continue

            contain.append([accu_time, accu_time + item.item_len() - 1, flag])
            accu_time += item.item_len()

        #在这里暂时不知道具体的广播运行机制
        #比如：是不是需要全部循环一遍来确定是否找到目标数据？
        #建议：读paper里关于index的部分



class ChannelGroupMember(object):

    global In

    def __init__(self,num,start,G_2 = None):

        self.G_2 = []

        for i in range(0,num):
            self.G_2.append(ChannelGroupItem(i+start))

    def print_member(self):
        for k in self.G_2:
            k.print_item()

    def get_G2(self):
        return self.G_2

    def member_len(self):
        return max(self.G_2, key = lambda x:x.item_len()).item_len()

    def total_data_len(self):
        return sum([x.data_len() for x in self.G_2])

    def append_dataGroup(self,g):
        sub = g.get_substream()

        for i in range(0,len(sub)):

            # Not combined
            if  not sub[i].is_combined():
                if sub[i].get_data_second_index() != -1:

                    # Insert the index
                    temp = DataGroupItem(sub[i].get_group_index(), sub[i].get_data_index(),\
                                            In, -2, sub[i].get_pieces())
                    self.G_2[i].insert_data(temp)
                    
                self.G_2[i].insert_data(sub[i])

            # Combined
            else:
                for x in sub[i].get_comlist():
                    if x.get_data_second_index() != -1:

                        # Add the index
                        temp = DataGroupItem(x.get_group_index(), x.get_data_index(), \
                                                In, -2, sub[i].get_pieces())
                        self.G_2[i].insert_data(temp)

                    self.G_2[i].insert_data(x)

        # insert the hole to occupy the channel
        m = max(self.G_2, key = lambda x:x.item_len()).item_len()
        
        for i in self.G_2:
            if i.item_len() < m:
                i.insert_data(DataGroupItem(-1,-1,m-i.item_len()))

    def has_data_group_member(data_group_member):
        for line in self.G_2:
            for item in line.get_chan_contain():
                if item.get_group_index() == data_group_member:
                    return True
        return False

    def access_time(data_group_member, level, start_time):

        members = len(self.G_2)

        temp_time = [0 for x in range(0, members)]

        for line in range(0, members):
            temp_time[line] = self.G_2[line].line_access_time(data_group_member, \
                                                            level, start_time)

        return max(temp_time)

    

class ChannelGroup(object):

    def __init__(self, num, G_3 = None):

        global T

        self.num = num
        self.G_3 = []

        for i in range(1,T+1):
            self.G_3.append(ChannelGroupMember(self.num,(i-1)*self.num+1))

    def print_groups(self):
        for i in range(1,T+1):
            print 'Group %d:' %(i)
            self.G_3[i-1].print_member()

    def print_grouplen(self):
        DG_index_list = []
        for x in self.G_3:
            DG_index = set([])
            for y in x.get_G2()[0].get_chan_contain():
                if y.get_group_index() > 0 and not (y.get_group_index() in DG_index):
                    DG_index.add(y.get_group_index())
            DG_index_list.append(DG_index)

        max = 0
        for i in range(1, T+1):
            temp = self.G_3[i-1].member_len()
            if temp > max:
                max = temp
            print 'Group %d: len %d' %(i, temp), DG_index_list[i-1]

    def get_maxlen(self):
        return max([x.member_len() for x in self.G_3])

    def min_member(self):
        return min(self.G_3, key = lambda x:x.member_len())

    def get_holelen(self):
        return sum([z.item_len() for x in self.G_3 for y in x.get_G2() \
                for z in y.get_chan_contain() if z.get_data_index() == -1])

    def get_totallen(self):
        return sum([y.item_len() for x in self.G_3 for y in x.get_G2()])

    def get_G3(self):
        return self.G_3

    def target_channel_length(data_group_member):
        for member in self.G_3:
            if member.has_data_group_member(data_group_member):
                return member.member_len()

    def access_target(data_group_member, level, start_time):
        for member in self.G_3:
            if member.has_data_group_member(data_group_member):
                return member.access_time(data_group_member, level, start_time)


##################################################################################
#                                                                                #
#                             ALGORITHM FUNCTIONS                                #
#                                                                                #
##################################################################################


# SDAA----------Simple Data Allocation Algorithm
# G_11 is the data group, X is the number of items in each data group member
def SDAA(G_11, X):

    global T, N, P

    T = N/X
    M = N/T
    
    G_1 = copy.deepcopy(G_11)

    G_1.sort_groups()
    
    CG = ChannelGroup(M)

    for i in range(0,P):
        s = CG.min_member()
        s.append_dataGroup(G_1.get_member(i))

    return CG


# ISDAA----------Improved Simple Data Allocation Algorithm

# The algorithm given by paper is not identical to the original algorithm!!!!!!!!!!!!!!
def SIZE(G):
    global T
    return max([sum([x.max_len() for x in G.get_G1()])/float(T), max([x.max_len() for x in G.get_G1()])])


def SCALE(G, d):
    temp = copy.deepcopy(G)
    for x in temp.get_G1():
        for i in x.get_substream():
            i.set_indexed_len(i.indexed_item_len()/float(d))

    return temp


# Function for L[u_1, ..., u_k]
def findInL(G, u):
    big = None
    first = True
    for x in G.get_G1():
        if x.max_len() <= u and first:
            big = x
            first = False
        if x.max_len() <= u and x.max_len() > big.max_len():
            big = x
    return big


'''
    The dual approximation algorithm for Bin Packing
    Returns [x, y]
    x is the total number of bins
    y is the actual schedual of bin-packing
'''

def DUAL(scaled_G_1):

    sG = copy.deepcopy(scaled_G_1)
    
    # The channel group is scalable here
    CG = []

    # Divide the data > 1/5 and <= 1/5

    sG_1 = DataGroup(True)
    sG_2 = DataGroup(True)

    count = 0
    count_1 = 0
    for x in sG.get_G1():
        count += 1
        if x.max_len() > 1/float(5):
            count_1 += 1
            sG_1.add_member(x)
        else:
            sG_2.add_member(x)

    percent = count_1*100/float(count)

    #logging.info('Len_1:%d Len_2:%d'%(len(sG_1.get_G1()), len(sG_2.get_G1())))

    '''
    The dual algorithm has two parts: one is the assumed algorithm to pack all
    of the pieces with size > 1/5; the other one is to pack the remaining pieces 
    of size <= 1/5.
    '''

    # Step 1: assumed algorithm 

    # Stage 1
    for x in sG_1.get_G1():
        if x.max_len() >= 0.6 and x.max_len() <= 1:
            y = findInL(sG_1, 1 - x.max_len())
            if y != None:
                CG.append([x, y])
                sG_1.del_member(y)
            else:
                CG.append([x])
            sG_1.del_member(x)


    # Stage 2
    for x in sG_1.get_G1():
        if x.max_len() >= 0.5 and x.max_len() < 0.6:
            hasY = False
            for y in sG_1.get_G1():
                if y.max_len() >= 0.5 and y.max_len() < 0.6 and \
                    y.get_memberIndex() != x.get_memberIndex():
                    hasY = True
                    CG.append([x, y])
                    sG_1.del_member(y)
                    break
            if not hasY:
                CG.append([x])
            sG_1.del_member(x)


    # Stage 3
    while len(sG_1.get_G1()) >= 1:
        x_3 = findInL(sG_1, 0.5)
        x_2 = findInL(sG_1, 0.4)
        x_1 = findInL(sG_1, 0.3)
        if x_1 == None or x_2 == None or x_3 == None or x_3.max_len() >= 0.4 or \
            x_3.get_memberIndex() == x_2.get_memberIndex() or \
            x_2.get_memberIndex() == x_1.get_memberIndex() or \
            x_1.get_memberIndex() == x_3.get_memberIndex():
            break
        temp = [x_1, x_2, x_3]
        CG.append(temp)
        sG_1.del_member(*temp)


    # Stage 4
    sG_1.get_G1().sort(key = lambda x:x.max_len(), reverse = True)
    while len(sG_1.get_G1()) >= 1:
        x_1 = sG_1.get_G1()[0]
        if x_1.max_len() < 0.4:
            break
        if len(sG_1.get_G1()) >= 2:
            temp = [x_1, sG_1.get_G1()[1]]
            CG.append(temp)
            sG_1.del_member(*temp)
        else:
            CG.append([x_1])
            sG_1.del_member(x_1)


    # Stage 5
    while len(sG_1.get_G1()) >= 1:

        sG_1.get_G1().sort(key = lambda x:x.max_len())
        small = sG_1.get_G1()[0]

        if small.max_len() <= 0.25:
            k = 0.25 - small.max_len()
            x_1 = findInL(sG_1, 0.25 + 3*k)
            x_2 = findInL(sG_1, 0.25 + k)
            x_3 = findInL(sG_1, 0.25 + k/3)
            temp_1 = [small, x_1, x_2, x_3]
            flag = False
            for x in range(0, 4):
                if temp_1[x] == None:
                    flag = True
                    break
                for y in range(x + 1, 4):
                    if temp_1[x].get_memberIndex() == temp_1[y].get_memberIndex():
                        flag = True
                        x = 4
                        break
            if not flag:
                CG.append(temp_1)
                sG_1.del_member(*temp_1)
                continue

        while len(sG_1.get_G1()) >= 3:
            small = sG_1.get_G1()[0]
            temp = [small, sG_1.get_G1()[1], sG_1.get_G1()[2]]
            CG.append(temp)
            sG_1.del_member(*temp)

        if len(sG_1.get_G1()) > 0:
            temp = []
            for x in sG_1.get_G1():
                temp.append(x)
            CG.append(temp)
            sG_1.del_member(*temp)
            

    # Step 2: remaining pieces with size <= 1/5

    #logging.info('Check: len(sG_1):%d len(sG_2):%d' %(len(sG_1.get_G1()),len(sG_2.get_G1())))

    #logging.info('sG_2 Len:%d'%len(sG_2.get_G1()))

    for remain in sG_2.get_G1():
        hasBin = False
        for bin in CG:
            if sum([x.max_len() for x in bin]) <= 1:
                hasBin = True
                bin.append(remain)
                break
        if not hasBin:
            CG.append([remain])

    return [len(CG), CG, percent]


# Improved SDAA using dual approximation algorithm
def ISDAA(DG_1, X):

    global T, N, P, Greater_Percent

    T = N/X
    M = N/T

    DG = copy.deepcopy(DG_1)

    lower = SIZE(DG)
    upper = 2*lower

    dual = 0

    while abs(upper - lower) > 0.0000000001:
        d = (upper+lower)/float(2)
        dual = DUAL(SCALE(DG, d))[0]
        if dual > T:
            lower = d
        else:
            upper = d

    answer = DUAL(SCALE(DG, upper))

    final = answer[1]

    Greater_Percent = answer[2]
    
    G_1 = copy.deepcopy(DG_1)

    CG = ChannelGroup(M)

    index = 0

    for line in final:
        Member = CG.get_G3()[index]
        temp = sum([x.max_len() for x in line])
        if temp > 1.2:
            print '----DUAL > 6/5: %.3f' % temp 
        index += 1
        for each in line:
            for select in DG.get_G1():
                if select.get_memberIndex() == each.get_memberIndex():
                    Member.append_dataGroup(select)

    return CG
            

# MDAA----------Modified Data Allocation Algorithm
def MDAA(Dmember):

    global K,U

    h = K

    G = copy.deepcopy(Dmember)

    while h <= U-1:
        I = max(G.get_substream(), key = lambda x:x.item_len())
        newlen_1 = I.item_len()/2
        newlen_2 = newlen_1
        if I.item_len() % 2 != 0:
            newlen_2 += 1

        i = I.get_data_second_index()
        I1 = DataGroupItem(I.get_group_index(), I.get_data_index(), newlen_1, i+1, 2)
        I2 = DataGroupItem(I.get_group_index(), I.get_data_index(), newlen_2, i+2, 2)

        G.del_item(I)
        G.add_item(I1)
        G.add_item(I2)

        h += 1

    return G


# AEA------------Average Estimation Algorithm
def AEA(Dmember):

    global U,K

    G = copy.deepcopy(Dmember)

    Temp = DataGroupMember(G.get_memberIndex())

    Temp.clear()

    #----------------Phase 1----------------

    h = U

    n = [0 for i in range(0,K)]

    A_ = 0.0
    
    A = sum([ x.item_len() for x in G.get_substream()]) / float(h)

    while A != A_ :

        A_ = A

        for x in range(0,K):
            s = G.get_substream()[x]
            if s.item_len() > 0 and s.item_len() <= A:
                q = copy.deepcopy(s)
                Temp.add_item(q)
                s.set_len(0)
                n[x] = 1
                h -= 1

        A = sum([x.item_len() for x in G.get_substream()])/float(h)

    Aw = int(math.ceil(A))

    #----------------Phase 2----------------

    for k in range(0,K):
        s = G.get_substream()[k]
        if s.item_len() > 0:

            n[k] = s.item_len()/Aw
            
            if s.item_len() % Aw == 0:
                s.set_pieces(n[k])
            else:
                s.set_pieces(n[k]+1)

            for i in range(0,n[k]):
                s.cut_len(Aw)

                if s.get_pieces() > 1:
                    s.set_data_second_index(s.get_data_second_index() + 1)
                    
                t = DataGroupItem(s.get_group_index(), s.get_data_index(), Aw,\
                                    s.get_data_second_index(), s.get_pieces())
                Temp.add_item(t)

            h -= n[k]


    #----------------Phase 3----------------
    
    max_item = 0
    max_index = 0

    # Available channel exists
    while h > 0:
        first = False

        # Find the max one
        for i in range(0,K):
            s = G.get_substream()[i]

            if s.item_len() > 0:    
                if not first:
                    max_item = s
                    max_index = i
                    first = True
                if s.item_len()/float(n[i]) > max_item.item_len()/float(n[max_index]):
                    max_item = s
                    max_index = i

        max_item.set_data_second_index(max_item.get_data_second_index() + 1)
        t = copy.deepcopy(max_item)
        Temp.add_item(t)
        max_item.set_len(0)

        n[max_index] += 1
        h -= 1

    # No available channel exists
    for i in range(0,K):
        s = G.get_substream()[i]

        if s.item_len() > 0:
        
            # Distributed value of remaining I_i
            value = s.item_len() / n[i]
            value_ = value
            assigned = False

            if s.item_len() % n[i] != 0:
                value_ += s.item_len() % n[i]

            # Assign value to the previous channels of I_i
            for j in Temp.get_substream():
                if j.get_data_index() == s.get_data_index():
                    if not assigned:
                        j.set_len(j.item_len() + value_)
                    else:
                        j.set_len(j.item_len() + value)
                    j.set_data_second_index(j.get_data_second_index() - 1)
                    j.set_pieces(j.get_pieces() - 1)

            # Delete I_i
            s.set_len(0)

    return Temp


# COA------------Channel Overlapping Algorithm
def COA(Dmember):

    global U,K,In

    Flag = True

    A = int(math.ceil(sum([x.item_len() for x in Dmember.get_substream()])/float(U)))

    Temp = 0

    while Flag:

        # logging.info('D:%d A:%d\n' %(Dmember.get_memberIndex(), A))

        Flag = False

        G = copy.deepcopy(Dmember)

        Temp = DataGroupMember(G.get_memberIndex())

        Temp.clear()

        f = [0 for i in range(0,K)]

        n = [0 for i in range(0,K)]


        #----------------Phase 1----------------

        for k in range(0,K):
            l = G.get_substream()[k]
            if l.item_len() <= A:
                f[k] = In
            else:
                f[k] = 0
            n[k] = int(math.floor(l.item_len()/float(A)))

            if l.item_len() % A == 0:
                l.set_pieces(n[k])
            else:
                l.set_pieces(n[k]+1)

            l.cut_len(n[k]*A)
            
            # Add item to Temp, each of the items has length of A
            for i in range(0,n[k]):

                if l.get_pieces() > 1:
                    l.set_data_second_index(l.get_data_second_index() + 1)

                t = DataGroupItem(l.get_group_index(), l.get_data_index(), A, \
                                    l.get_data_second_index(), l.get_pieces())
                Temp.add_item(t)

        h = U - sum([x for x in n])

        # After phase 1, data len correct

        #----------------Phase 2----------------
        # Insert the remaining l as a whole, then set l to 0.

        G.get_substream().sort(key = lambda x:x.item_len(), reverse = True)

        d = [A + In for j in range(0,h)]

        X = [[] for j in range(0,h)]

        for k in range(0,K):
            l = G.get_substream()[k]

            if l.item_len() > 0:
                for j in range (0,h):
                    if l.item_len() + In - f[k] <= d[j]:
                        d[j] -= l.item_len() + In - f[k]

                        if l.get_pieces() > 1:
                            l.set_data_second_index(l.get_data_second_index() + 1)
                        t = copy.deepcopy(l)
                        X[j].append(t)

                        l.set_len(0)

                        break

        # After phase 2, data len correct


        #----------------Phase 3----------------
        # now we have to divide each l into pieces (at least 2 pieces) and insert them

        for k in range(0, K):
            p = sum([1 for j in range(0,h) if d[j] > In])

            l = G.get_substream()[k]

            total = sum([x for x in d if x > In])

            if l.item_len() > 0:

                # logging.info('---before phase 3: G:%d D:%d L:%d' %(G.get_memberIndex(), \
                #               l.get_data_index(), l.item_len()))
                # logging.info('------p:%d total:%d' %(p, total))
                # logging.info('------<=: %r' % (l.item_len() + p*In <= total))

                if l.item_len() + p*In <= total and p > 0:
                    # l can be split with d_j to fill available channels

                    for j in range(0,h):
                        if d[j] > In:
                            if l.item_len() > d[j] - In:

                                # Every l > d[j] - In, need add index, split l, and increase 
                                # the second index and pieces
                                l.set_data_second_index(l.get_data_second_index() + 1)
                                l.set_pieces(l.get_pieces() + 1)

                                # Need to update pieces in Temp and X
                                for item in Temp.get_substream():
                                    if item.get_data_index() == l.get_data_index():
                                        item.set_pieces(l.get_pieces())

                                for q in X:
                                    for u in q:
                                        if u.get_data_index() == l.get_data_index():
                                            u.set_pieces(l.get_pieces())                         

                                t = DataGroupItem(l.get_group_index(), l.get_data_index(), d[j] - In,\
                                                     l.get_data_second_index(), l.get_pieces())
                                X[j].append(t)

                                l.cut_len(d[j] - In)

                                # logging.info('---middle_1 phase 3: G:%d D:%d L:%d d[j]:%d' \
                                #   %(G.get_memberIndex(), l.get_data_index(), l.item_len(), d[j]))
                                
                                d[j] = In
                                if l.item_len() == 0:
                                    break

                            else:
                                t = DataGroupItem(l.get_group_index(), l.get_data_index(), l.item_len(),\
                                                    l.get_data_second_index(), l.get_pieces())
                                X[j].append(t)

                                l.set_len(0)

                                # logging.info('---middle_2 phase 3: G:%d D:%d L:%d d[j]:%d' 
                                #           %(G.get_memberIndex(), l.get_data_index(), l.item_len(), d[j]))
                                
                                d[j] -= l.item_len()

                                break
                            
                else:
                    # We have to set A = A + 1, goto Phase 1
                    A += 1
                    Flag = True
                    break

                # logging.info('---after phase 3: G:%d D:%d L:%d' %(G.get_memberIndex(),\
                #               l.get_data_index(), l.item_len()))

        if not Flag:

            # Handle X here
            for i in X:
                # only one item
                if len(i) == 1:
                    t = copy.deepcopy(i[0])
                    Temp.add_item(t)
                # several items, need to use comList
                elif len(i) > 1:
                    t = DataGroupItem(-1, -1, -1, -1, -1, True, i)
                    Temp.add_item(t)
                i[:] = []

    if temp_len(Temp) != origin_len(Dmember):
        logging.info('G:%d not same.'%Dmember.get_memberIndex())

    return Temp


##################################################################################
#                                                                                #
#                                DEBUGGING TOOLS                                 #
#                                                                                #
##################################################################################    

def data_checker(CG_1, DG_1):

    CG = copy.deepcopy(CG_1)
    DG = copy.deepcopy(DG_1)

    len_temp = 0

    for Dmember in DG.get_G1():
        len_temp += Dmember.total_len()

    for Cmember in CG.get_G3():
        len_temp -= Cmember.total_data_len()

    return len_temp

def temp_len(Temp):
    l = 0
    for x in Temp.get_substream():
        l += x.item_len()
    return l

def origin_len(G):
    return sum([x.item_len() for x in G.get_substream()])


##################################################################################
#                                                                                #
#                         ALGORITHM IMPLEMENTATION                               #
#                                                                                #
##################################################################################

'''
    Using index to indicate the function you choose:
    0: pure SDAA
    1: pure ISDAA
    2: SDAA-MDAA
    3: ISDAA-MDAA
    4: SDAA-AEA
    5: ISDAA-AEA
    6: SDAA-COA
    7: ISDAA-COA
'''

func_list = ((SDAA, None, 'SDAA'), (ISDAA, None, 'ISDAA'), \
            (SDAA, MDAA, 'SDAA-MDAA'), (ISDAA, MDAA, 'ISDAA-MDAA'), \
            (SDAA, AEA, 'SDAA-AEA'), (ISDAA, AEA, 'ISDAA-AEA'), \
            (SDAA, COA, 'SDAA-COA'), (ISDAA, COA, 'ISDAA-COA'))


'''
    Generate a tuple of Data Groups: (G, G1, G2, G3)
    G for SDAA(ISDAA)
    G1 for MDAA
    G2 for AEA
    G3 for COA
'''

def generate_data_groups(print_data):

    # Original data group
    G = DataGroup(False)

    if print_data:
        print '\n------------------\nOriginal data group:'
        G.print_groups()

    # Empty data group
    G1 = DataGroup(True)
    G2 = DataGroup(True)
    G3 = DataGroup(True)

    for i in range(0,P):

        # Using MDAA to append member to G1
        I_1 = copy.deepcopy(MDAA(G.get_member(i)))
        G1.add_member(I_1)

        # Using AEA to append member to G2
        I_2 = copy.deepcopy(AEA(G.get_member(i)))
        G2.add_member(I_2)

        # Using COA to append member to G3
        I_3 = copy.deepcopy(COA(G.get_member(i)))
        G3.add_member(I_3)

    return (G, G1, G2, G3)


'''
    Run the function 'num' in the 'func_list' once

    To print the result:
        0: print nothing
        1: print the distribution whole channel group
        2: print the length of the channel group
        3: print the maximum lenght of the channel group

    *G: (G, G1, G2, G3)

    Return the distributed channel group
'''

def select_func(num, print_result, G):

    global K, U

    select = func_list[num]

    Group = 0
    limit = 0

    if select[1] == None:
        limit = K
        Group = G[0]
    else:
        limit = U
        if select[1] == MDAA:
            Group = G[1]
        elif select[1] == AEA:
            Group = G[2]
        else:
            Group = G[3]

    if print_result != 0:
        print '\n-----------------------\n%s:' %select[2]

    run = select[0](Group,limit)

    temp = data_checker(run, Group)
    if temp != 0:
        print('%s wrong result:%d' %(select[2], temp))


    if print_result == 1:
        run.print_groups()
    if print_result == 2:
        run.print_grouplen()
    if print_result == 3:
        print 'Max:', run.get_maxlen()

    # if num % 2 == 1:
        # print 'Final percentage of > 1/5: %.2f%%' %Greater_Percent

    return run


'''
    Set the parameters
    N_1:    No. of the channels in the system
    P_1:    No. of the data group members in a program
    K_1:    No. of quality requirements
    U_1:    Channel constraint for one client
    In_1:   Channel broadcast rate
    mu_1:   Average size for multimedia files
    sig_1:  Variance among multimedia files
'''

def set_param(N_1, P_1, K_1, U_1, In_1, mu_1, sig_1):

    global N, P, K, U, In, R, mu, sig

    N = N_1
    P = P_1
    K = K_1
    U = U_1
    In = In_1
    mu = mu_1
    sig = sig_1



##################################################################################
#                                                                                #
#                           PERFORMANCE EVALUATION                               #
#                                                                                #
##################################################################################

'''
    Run the 8 algorithms for 'iter' times each, using the same data group

    'option': 
        0. average makespan  
        1. average channel length
        2. average unused channel length
        3. percentage of average unused channel length
'''

def average_criterion(option, iter):

    global N

    ChannelLength = [0 for index in range(0, 8)]

    proceed = 0

    for times in range(0, iter):

        proceed += 1

        if proceed * 100 / iter % 5 == 0:
            print 'Proceed: %d%%' %(proceed *100 / iter)

        Groups = generate_data_groups(False)

        for index in range(0, 8):
            CG = select_func(index, 0, Groups)
            if option == 0:
                ChannelLength[index] += CG.get_maxlen()
            if option == 1:
                ChannelLength[index] += CG.get_totallen()/N
            if option == 2:
                ChannelLength[index] += CG.get_holelen()
            if option == 3:
                ChannelLength[index] += CG.get_holelen() * 100/float(CG.get_totallen())
    for index in range(0, 8):
        ChannelLength[index] /= iter

    if option == 0:
        print '\nAverage makespan for iteration %d:' %iter
    elif option == 1:
        print '\nAverage channel length for iteration %d:' %iter
    elif option == 2:
        print '\nAverage unused channel length for iteration %d:' %iter

    if option == 0 or option == 1 or option == 2:
        print '''SDAA:\t\t%d\nISDAA:\t\t%d
            \nSDAA-MDAA:\t%d\nISDAA-MDAA:\t%d
            \nSDAA-AEA:\t%d\nISDAA-AEA:\t%d
            \nSDAA-COA:\t%d\nISDAA-COA:\t%d''' %(tuple(ChannelLength))

    if option == 3:
        print '\nAverage percentage of unused channel length for iteration %d:' %iter
        print '''SDAA:\t\t%.2f%%\nISDAA:\t\t%.2f%%
            \nSDAA-MDAA:\t%.2f%%\nISDAA-MDAA:\t%.2f%%
            \nSDAA-AEA:\t%.2f%%\nISDAA-AEA:\t%.2f%%
            \nSDAA-COA:\t%.2f%%\nISDAA-COA:\t%.2f%%''' %(tuple(ChannelLength))


def sim_access_time(channel_group, data_group_member, level, iter):

    access_time = 0

    for time in range(0, iter):
        start = random.randint(0, channel_group.target_channel_length(data_group_member))

        access_time += channel_group.access_target(data_group_member, level, start)


    

'''
    Simulate a user to access the broadcasting system for 'iter' times

    Each time the user will ask for a certain piece of data, which means he must
download the whole data group member of that data

    Calculate the avreage access time of the user in 'iter' times when using a 
certain algorithm
'''

def access_time_criterion(iter):
    
    global N, P, K, U

    access_time = [[0 for index in range(0, 8)] for index in range(0, K)]

    proceed = 0

    for times in range(0, iter):

        proceed += 1

        if proceed * 100 / iter % 5 == 0:
            print 'Proceed: %d%%' %(proceed * 100 / iter)

        groups = generate_data_groups(False)

        

##################################################################################
#                                                                                #
#                                MAIN FUNCTION                                   #
#                                                                                #
##################################################################################

def main():

    '''
        Set the parameters
        N_1:    No. of the channels in the system
        P_1:    No. of the data group members in a program
        K_1:    No. of quality requirements
        U_1:    Channel constraint for one client
        In_1:   Length of the index
        mu_1:   Average size for multimedia files
        sig_1:  Variance among multimedia files
    '''

    set_param(10, 6, 3, 5, 1, 4*1024, 5)

    average_criterion(3, 20)
    

if __name__ == '__main__':
    main()
    



    

        

