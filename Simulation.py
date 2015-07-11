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

#No. of the channels in the system
N = 10

#No. of the data items in a program
P = 6

#No. of quality requirements
K = 3

#Channel constraint for one client
U = 5

#Channel broadcast rate
R = 100

#No. of channel groups T = N/K or T = N/U
T = 0

#Group of data groups
G = []

#Length of the index
In = 1

##################################################################################
#                                                                                #
#                              CLASS DEFINITIONS                                 #
#                                                                                #
##################################################################################


#############################      DATA GROUP     ################################

class DataGroupItem(object):

    def __init__(self, Gindex, Dindex, length, Sindex = -1, Pieces = 1, Combined = False, ComList = None):

        #Dindex: -1 hole
        #1,2... data     
        self.data_index = Dindex

        #Sindex: -1 only one piece
        #-2 index
        #0,1,2... more than one pieces
        self.data_second_index = Sindex

        self.data_length = length

        #Gindex: -1 hole
        #1,2... data
        self.group_index = Gindex

        #Combined: False only one piece
        #True several pieces are combined together
        #ComList is used to pass the list where the pieces are stored
        self.combined = Combined
        self.comlist = copy.deepcopy(ComList)

        #Pieces: No. of pieces a data is divided into
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
            print '    G%d Q%d S%d P%d: %d'%(self.group_index, self.data_index, self.data_second_index, self.pieces, self.data_length)
        else:
            print '    Combined:'
            for x in range(0,len(self.comlist)):
                print '      G%d Q%d S%d P%d: %d'%(self.comlist[x].group_index, self.comlist[x].data_index, self.comlist[x].data_second_index, self.comlist[x].pieces, self.comlist[x].data_length)

    def item_len(self):
        return self.data_length

    def set_len(self,x):
        self.data_length = x

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

        #Generate the items of a data group
        #Here using random generation-------------------------need modification
        #The range is (30,100), because of the requirement of 1/5 approximation algorithm in ISDAA
        for j in range(1,K+1):
            self.subStream.append(DataGroupItem(self.member_index, j, random.randint(30,100)))

    def print_member(self):
        for i in self.subStream:
            i.print_item()

    def max_len(self):
        return max(self.subStream, key = lambda x:x.item_len()).item_len()

    def total_len(self):
        temp_len = 0
        for x in self.subStream:
            if x.combined:
                for y in x.get_comlist():
                    temp_len += y.item_len()
            else:
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

            #Generate the Group of data groups
            #Here using random generation-------------------------need modification
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
        return sum([x.item_len() for x in self.chan_contain if x.get_data_index() > 0 and x.get_data_second_index() > -2 ])

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

            #Not combined
            if  not sub[i].is_combined():
                if sub[i].get_data_second_index() != -1:

                    #Insert the index
                    temp = DataGroupItem(sub[i].get_group_index(), sub[i].get_data_index(), In, -2, sub[i].get_pieces())
                    self.G_2[i].insert_data(temp)
                    
                self.G_2[i].insert_data(sub[i])

            #Combined
            else:
                for x in sub[i].get_comlist():
                    if x.get_data_second_index() != -1:

                        #Add the index
                        temp = DataGroupItem(x.get_group_index(), x.get_data_index(), In, -2, sub[i].get_pieces())
                        self.G_2[i].insert_data(temp)

                    self.G_2[i].insert_data(x)

        #insert the hole to occupy the channel
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
            print '\nGroup %d:' %(i)
            self.G_3[i-1].print_member()

    def print_grouplen(self):
        for i in range(1, T+1):
            print '\nGroup %d: len %d' %(i, self.G_3[i-1].member_len())

    def min_member(self):
        return min(self.G_3, key = lambda x:x.member_len())

    def get_G3(self):
        return self.G_3


##################################################################################
#                                                                                #
#                             ALGORITHM FUNCTIONS                                #
#                                                                                #
##################################################################################


#SDAA----------Simple Data Allocation Algorithm
#G_11 is the data group, X is the number of items in each data group member
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

    print '\nThe assigned channel groups are:'
    #CG.print_groups()
    CG.print_grouplen()

    return CG



#ISDAA----------Improved Simple Data Allocation Algorithm

#The algorithm given by paper is not identical to the original algorithm!!!!!!!!!!!!!!
def SIZE(G,P):
    return max([sum([x.max_len() for x in G])/float(P), max([x.max_len() for x in G])])

def DUAL(G, d, X):
    global T, N, P, U, K

    T = N/X
    M = N/T

    Temp = copy.deepcopy(G)

    #Scale the pieces
    for x in Temp.get_G1():
        for i in x.get_substream():
            x.set_len(x.item_len()/float(d))

    CG = ChannelGroup(M)
    
    


def ISDAA(DG_1, CG_1, P, M, T):
    DG = copy.deepcopy(DG_1)
    CG = copy.deepcopy(CG_1)

    lower = SIZE(DG,P)
    upper = 2*lower

    while upper != lower:
        d = (upper+lower)/float(2)
        dual = DUAL(DG, d)
        if dual > P:
            lower = d
        else:
            upper = d
    
    output = upper

    DUAL(DG, output)

    return output




#MDAA----------Modified Data Allocation Algorithm
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



#AEA------------Average Estimation Algorithm
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
                    
                t = DataGroupItem(s.get_group_index(), s.get_data_index(), Aw, s.get_data_second_index(), s.get_pieces())
                Temp.add_item(t)

            h -= n[k]


    #----------------Phase 3----------------
    
    max_item = 0
    max_index = 0

    #Available channel exists
    while h > 0:
        first = False

        #Find the max one
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

    #No available channel exists
    for i in range(0,K):
        s = G.get_substream()[i]

        if s.item_len() > 0:
        
            #Distributed value of remaining I_i
            value = s.item_len() / n[i]
            value_ = value
            assigned = False

            if s.item_len() % n[i] != 0:
                value_ += s.item_len() % n[i]

            #Assign value to the previous channels of I_i
            for j in Temp.get_substream():
                if j.get_data_index() == s.get_data_index():
                    if not assigned:
                        j.set_len(j.item_len() + value_)
                    else:
                        j.set_len(j.item_len() + value)
                    j.set_data_second_index(j.get_data_second_index() - 1)
                    j.set_pieces(j.get_pieces() - 1)

            #Delete I_i
            s.set_len(0)

    return Temp



#COA------------Channel Overlapping Algorithm
def COA(Dmember):

    global U,K,In

    Flag = True

    A = int(math.ceil(sum([x.item_len() for x in Dmember.get_substream()])/float(U)))

    Temp = 0

    while Flag:

        #logging.info('D:%d A:%d\n' %(Dmember.get_memberIndex(), A))

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
            
            #Add item to Temp, each of the items has length of A
            for i in range(0,n[k]):

                if l.get_pieces() > 1:
                    l.set_data_second_index(l.get_data_second_index() + 1)

                t = DataGroupItem(l.get_group_index(), l.get_data_index(), A, l.get_data_second_index(), l.get_pieces())
                Temp.add_item(t)

        h = U - sum([x for x in n])

        #After phase 1, data len correct

        #----------------Phase 2----------------
        #Insert the remaining l as a whole, then set l to 0.

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

        #After phase 2, data len correct


        #----------------Phase 3----------------
        #now we have to divide each l into pieces (at least 2 pieces) and insert them

        for k in range(0, K):
            p = sum([1 for j in range(0,h) if d[j] > In])

            l = G.get_substream()[k]

            total = sum([x for x in d if x > In])

            if l.item_len() > 0:

                #logging.info('---before phase 3: G:%d D:%d L:%d' %(G.get_memberIndex(), l.get_data_index(), l.item_len()))
                #logging.info('------p:%d total:%d' %(p, total))
                #logging.info('------<=: %r' % (l.item_len() + p*In <= total))

                if l.item_len() + p*In <= total and p > 0:
                    #l can be split with d_j to fill available channels

                    for j in range(0,h):
                        if d[j] > In:
                            if l.item_len() > d[j] - In:

                                #Every l > d[j] - In, need add index, split l, and increase the second index and pieces
                                l.set_data_second_index(l.get_data_second_index() + 1)
                                l.set_pieces(l.get_pieces() + 1)

                                #Need to update pieces in Temp and X
                                for item in Temp.get_substream():
                                    if item.get_data_index() == l.get_data_index():
                                        item.set_pieces(l.get_pieces())

                                for q in X:
                                    for u in q:
                                        if u.get_data_index() == l.get_data_index():
                                            u.set_pieces(l.get_pieces())                         

                                t = DataGroupItem(l.get_group_index(), l.get_data_index(), d[j] - In, l.get_data_second_index())
                                X[j].append(t)

                                l.cut_len(d[j] - In)

                                #logging.info('---middle_1 phase 3: G:%d D:%d L:%d d[j]:%d' %(G.get_memberIndex(), l.get_data_index(), l.item_len(), d[j]))
                                
                                d[j] = In
                                if l.item_len() == 0:
                                    break

                            else:
                                t = DataGroupItem(l.get_group_index(), l.get_data_index(), l.item_len(), l.get_data_second_index())
                                X[j].append(t)

                                l.set_len(0)

                                #logging.info('---middle_2 phase 3: G:%d D:%d L:%d d[j]:%d' %(G.get_memberIndex(), l.get_data_index(), l.item_len(), d[j]))
                                
                                d[j] -= l.item_len()

                                break
                            
                else:
                    #We have to set A = A + 1, goto Phase 1
                    A += 1
                    Flag = True
                    break

                #logging.info('---after phase 3: G:%d D:%d L:%d' %(G.get_memberIndex(), l.get_data_index(), l.item_len()))

        if not Flag:

            #Handle X here
            for i in X:
                #only one item
                if len(i) == 1:
                    t = copy.deepcopy(i[0])
                    Temp.add_item(t)
                #several items, need to use comList
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
        if x.combined:
            for y in x.get_comlist():
                l += y.item_len()
        else:
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

    #Original data group
    G = DataGroup(False)

    print '\n------------------\nOriginal data group:'
    G.print_groups()

    #Empty data group
    G1 = DataGroup(True)
    G2 = DataGroup(True)
    G3 = DataGroup(True)

    #Using MDAA to append member to G1
    for i in range(0,P):
        I = copy.deepcopy(MDAA(G.get_member(i)))
        G1.add_member(I)

    #Using AEA to append member to G2
    for i in range(0,P):
        I = copy.deepcopy(AEA(G.get_member(i)))
        G2.add_member(I)


    #Using COA to append member to G3
    for i in range(0,P):
        I = copy.deepcopy(COA(G.get_member(i)))
        G3.add_member(I)

    print '\n-----------------------\n SDAA assignment result:'

    print('SDAA len diff:%d' %data_checker(SDAA(G,K), G))

    print '\n-----------------------\n MDAA assignment result:'

    print('MDAA len diff:%d' %data_checker(SDAA(G1,U), G1))

    print '\n-----------------------\n AEA assignment result:'

    print('AEA len diff:%d' %data_checker(SDAA(G2,U), G2))

    print '\n-----------------------\n COA assignment result:'

    print('COA len diff:%d' %data_checker(SDAA(G3,U), G3))


        

