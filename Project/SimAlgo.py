import math
import copy
from SimDebugTool import origin_len, temp_len
import GlobalVar
from ChannelGroup import ChannelGroup, ChannelGroupMember, ChannelGroupItem
from DataGroup import DataGroup, DataGroupMember, DataGroupItem



# SDAA----------Simple Data Allocation Algorithm
# G_11 is the data group, X is the number of items in each data group member
def SDAA(G_11, X):


    GlobalVar.T = GlobalVar.N/X
    M = GlobalVar.N/GlobalVar.T
    
    G_1 = copy.deepcopy(G_11)

    G_1.sort_groups()
    
    CG = ChannelGroup(M)

    for i in range(0,GlobalVar.P):
        s = CG.min_member()
        s.append_dataGroup(G_1.get_member(i))

    return CG


# ISDAA----------Improved Simple Data Allocation Algorithm

# The algorithm given by paper is not identical to the original algorithm!!!!!!!!!!!!!!
def SIZE(G):

    return max([sum([x.max_len() for x in G.get_G1()])/float(GlobalVar.T), max([x.max_len() for x in G.get_G1()])])


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

    GlobalVar.T = GlobalVar.N/X
    M = GlobalVar.N/GlobalVar.T

    DG = copy.deepcopy(DG_1)

    lower = SIZE(DG)
    upper = 2*lower

    dual = 0

    while abs(upper - lower) > 0.0000000001:
        d = (upper+lower)/float(2)
        dual = DUAL(SCALE(DG, d))[0]
        if dual > GlobalVar.T:
            lower = d
        else:
            upper = d

    answer = DUAL(SCALE(DG, upper))

    final = answer[1]

    GlobalVar.Greater_Percent = answer[2]
    
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

    h = GlobalVar.K

    G = copy.deepcopy(Dmember)

    while h <= GlobalVar.U-1:
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

    G = copy.deepcopy(Dmember)

    Temp = DataGroupMember(G.get_memberIndex())

    Temp.clear()

    #----------------Phase 1----------------

    h = GlobalVar.U

    n = [0 for i in range(0,GlobalVar.K)]

    A_ = 0.0
    
    A = sum([ x.item_len() for x in G.get_substream()]) / float(h)

    while A != A_ :

        A_ = A

        for x in range(0,GlobalVar.K):
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

    for k in range(0,GlobalVar.K):
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
        for i in range(0,GlobalVar.K):
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
    for i in range(0,GlobalVar.K):
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

    Flag = True

    A = int(math.ceil(sum([x.item_len() for x in Dmember.get_substream()])/float(GlobalVar.U)))

    Temp = 0

    while Flag:

        # logging.info('D:%d A:%d\n' %(Dmember.get_memberIndex(), A))

        Flag = False

        G = copy.deepcopy(Dmember)

        Temp = DataGroupMember(G.get_memberIndex())

        Temp.clear()

        f = [0 for i in range(0,GlobalVar.K)]

        n = [0 for i in range(0,GlobalVar.K)]


        #----------------Phase 1----------------

        for k in range(0,GlobalVar.K):
            l = G.get_substream()[k]
            if l.item_len() <= A:
                f[k] = GlobalVar.In
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

        h = GlobalVar.U - sum([x for x in n])

        # After phase 1, data len correct

        #----------------Phase 2----------------
        # Insert the remaining l as a whole, then set l to 0.

        G.get_substream().sort(key = lambda x:x.item_len(), reverse = True)

        d = [A + GlobalVar.In for j in range(0,h)]

        X = [[] for j in range(0,h)]

        for k in range(0,GlobalVar.K):
            l = G.get_substream()[k]

            if l.item_len() > 0:
                for j in range (0,h):
                    if l.item_len() + GlobalVar.In - f[k] <= d[j]:
                        d[j] -= l.item_len() + GlobalVar.In - f[k]

                        if l.get_pieces() > 1:
                            l.set_data_second_index(l.get_data_second_index() + 1)
                        t = copy.deepcopy(l)
                        X[j].append(t)

                        l.set_len(0)

                        break

        # After phase 2, data len correct


        #----------------Phase 3----------------
        # now we have to divide each l into pieces (at least 2 pieces) and insert them

        for k in range(0, GlobalVar.K):
            p = sum([1 for j in range(0,h) if d[j] > GlobalVar.In])

            l = G.get_substream()[k]

            total = sum([x for x in d if x > GlobalVar.In])

            if l.item_len() > 0:

                # logging.info('---before phase 3: G:%d D:%d L:%d' %(G.get_memberIndex(), \
                #               l.get_data_index(), l.item_len()))
                # logging.info('------p:%d total:%d' %(p, total))
                # logging.info('------<=: %r' % (l.item_len() + p*GlobalVar.In <= total))

                if l.item_len() + p*GlobalVar.In <= total and p > 0:
                    # l can be split with d_j to fill available channels

                    for j in range(0,h):
                        if d[j] > GlobalVar.In:
                            if l.item_len() > d[j] - GlobalVar.In:

                                # Every l > d[j] - GlobalVar.In, need add index, split l, and increase 
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

                                t = DataGroupItem(l.get_group_index(), l.get_data_index(), d[j] - GlobalVar.In,\
                                                     l.get_data_second_index(), l.get_pieces())
                                X[j].append(t)

                                l.cut_len(d[j] - GlobalVar.In)

                                # logging.info('---middle_1 phase 3: G:%d D:%d L:%d d[j]:%d' \
                                #   %(G.get_memberIndex(), l.get_data_index(), l.item_len(), d[j]))
                                
                                d[j] = GlobalVar.In
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