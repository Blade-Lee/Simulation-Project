import random
import copy
import GlobalVar
import sys, os
import json

class DataGroupItem(object):

    def __init__(self, Gindex, Dindex, length, Sindex = -1, Pieces = 1, \
                    Combined = False, ComList = None):

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
                self.data_indexed_length += GlobalVar.In

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

    def __init__(self, Gindex, qualities = None):

        self.subStream = []
        self.member_index = Gindex

        # Generate the items of a data group
        # Here using random generation-------------------------need modification
        # The range is (30,100), because of the requirement of 
        # 1/5 approximation algorithm in ISDAA
        if qualities != None:
            for j in range(1, GlobalVar.K + 1):
                self.subStream.append(DataGroupItem(self.member_index, j, \
                                                qualities[GlobalVar.K - j]))

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
    
    def __init__(self, empty):

        self.G_1 = []
        
        if empty == False:

            load_file_path = os.path.join(sys.path[0] + "\..\data\Quality_Video_data")

            with open(load_file_path, "r") as read_file:
                quality_data = json.load(read_file)
                for i in range(1, GlobalVar.P + 1):
                    self.G_1.append(DataGroupMember(i, quality_data[i-1]))

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