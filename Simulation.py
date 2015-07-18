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
N = 20

# No. of the data items in a program
P = 100

# No. of quality requirements
K = 4

# Channel constraint for one client
U = 5

# Channel broadcast rate
R = 100

# No. of channel groups T = N/K or T = N/U
T = 0

# Group of data groups
G = []

# Length of the index
In = 1

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
        self.subStream = []
        self.member_index = Gindex

        # Generate the items of a data group
        # Here using random generation-------------------------need modification
        # The range is (30,100), because of the requirement of 
        # 1/5 approximation algorithm in ISDAA
        for j in range(1,K+1):
            self.subStream.append(DataGroupItem(self.member_index, j, \
                random.randint(30,100)))

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

class ChannelGroupMember(object):

    global In

    def __init__(self,num,start,G_2 = None):

        self.G_2 = []

        for i in range(0,num):
            self.G_2.append(ChannelGroupItem(i+start))

    def print_member(self):
        for k in self.G_2:
            k.print_item()

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
        max = 0
        for i in range(1, T+1):
            temp = self.G_3[i-1].member_len()
            if temp > max:
                max = temp
            print 'Group %d: len %d' %(i, temp)
        print 'Max: %d' %max

    def min_member(self):
        return min(self.G_3, key = lambda x:x.member_len())

    def get_G3(self):
        return self.G_3


##################################################################################
#                                                                                #
#                             ALGORITHM FUNCTIONS                                #
#                                                                                #
##################################################################################


# SDAA----------Simple Data Allocation Algorithm
# G_11 is the data group, X is the number of items in each data group member
def SDAA(G_11,X):

    global T, N, P

    T = N/X
    M = N/T
    
    G_1 = copy.deepcopy(G_11)

    G_1.sort_groups()
    
    CG = ChannelGroup(M)

    for i in range(0,P):
        s = CG.min_member()
        s.append_dataGroup(G_1.get_member(i))

    # print '\nThe assigned channel groups are:'
    #CG.print_groups()
    CG.print_grouplen()

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

# The dual approximation algorithm for Bin Packing
# Returns [x, y]
# x is the total number of bins
# y is the actual schedual of bin-packing
def DUAL(scaled_G_1):

    sG = copy.deepcopy(scaled_G_1)
    
    # The channel group is scalable here
    CG = []

    # Divide the data > 1/5 and <= 1/5

    sG_1 = DataGroup(True)
    sG_2 = DataGroup(True)

    for x in sG.get_G1():
        if x.max_len() > 1/float(5):
            sG_1.add_member(x)
        else:
            sG_2.add_member(x)

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

    return [len(CG), CG]

# Improved SDAA using dual approximation algorithm
def ISDAA(DG_1, X):

    global T, N, P

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

    final = DUAL(SCALE(DG, upper))[1]
    
    #print '++++++++++++++++++++++++++++\n'
    #print 'dual:%d T:%d upper:%.10f lower:%.10f'%(dual, T, upper, lower)
    '''
    for x in range(0, len(final)):
        print 'Line %d:'%(x+1)
        for y in final[x]:
            print '\tMemberIndex:%d' %y.get_memberIndex()
        print'\tLen:%.10f' %sum([y.max_len() for y in final[x]])
    '''
    G_1 = copy.deepcopy(DG_1)

    CG = ChannelGroup(M)

    index = 0

    for line in final:
        Member = CG.get_G3()[index]
        index += 1
        for each in line:
            for select in DG.get_G1():
                if select.get_memberIndex() == each.get_memberIndex():
                    Member.append_dataGroup(select)

    #CG.print_groups()
    CG.print_grouplen()

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

if __name__ == '__main__':

    # Original data group
    G = DataGroup(False)

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
        

    ###################### original ########################
    
    print '\n-----------------------\nSDAA:'
    temp = data_checker(SDAA(G,K), G)
    if temp != 0:
        print('SDAA wrong result:%d' %temp)

    print '\nISDAA:'
    temp = data_checker(ISDAA(G,K), G)
    if temp != 0:
        print('ISDAA wrong result:%d' %temp)

    ######################## MDAA ############################

    print '\n-----------------------\nSDAA  MDAA:'
    temp = data_checker(SDAA(G1,U), G1)
    if temp != 0:
        print('SDAA MDAA wrong result:%d' %temp)

    print '\nISDAA  MDAA:'
    temp = data_checker(ISDAA(G1,U), G1)
    if temp != 0:
        print('ISDAA MDAA wrong result:%d' %temp)

    ######################### AEA ###########################

    print '\n-----------------------\nSDAA  AEA:'
    temp = data_checker(SDAA(G2,U), G2)
    if temp != 0:
        print('SDAA AEA wrong result:%d' %temp)

    print '\nISDAA  AEA:'
    temp = data_checker(ISDAA(G2,U), G2)
    if temp != 0:
        print('ISDAA AEA wrong result:%d' %temp)

    ######################### COA ###########################
    
    print '\n-----------------------\nSDAA  COA:'
    temp = data_checker(SDAA(G3,U), G3)
    if temp != 0:
        print('SDAA COA wrong result:%d' %temp)

    print '\nISDAA  COA:'
    temp = data_checker(ISDAA(G3,U), G3)
    if temp != 0:
        print('ISDAA COA wrong result:%d' %temp)



    

        

