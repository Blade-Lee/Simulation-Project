from DataGroup import DataGroupItem
import GlobalVar 

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

    def has_data(self, data_group_member, level):
        for item in self.chan_contain:
                if item.get_group_index() == data_group_member and\
                    item.get_data_index() <= level:
                    return True
        return False

    def line_access_time(self, data_group_member, level, start_time):

        contain = []
        accu_time = 0
        flag = False

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

        #index has no help on broadcasting simulation

        time_min = self.chan_length
        for item in contain:
            if item[0] < start_time and item[1] >= start_time:
                if item[2]:
                    time_min += item[1] - start_time + 1
                else:
                    time_min -= start_time - item[0] + 1
                break

        return time_min 




class ChannelGroupMember(object):

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
                                            GlobalVar.In, -2, sub[i].get_pieces())
                    self.G_2[i].insert_data(temp)
                    
                self.G_2[i].insert_data(sub[i])

            # Combined
            else:
                for x in sub[i].get_comlist():
                    if x.get_data_second_index() != -1:

                        # Add the index
                        temp = DataGroupItem(x.get_group_index(), x.get_data_index(), \
                                                GlobalVar.In, -2, sub[i].get_pieces())
                        self.G_2[i].insert_data(temp)

                    self.G_2[i].insert_data(x)

        # insert the hole to occupy the channel
        m = max(self.G_2, key = lambda x:x.item_len()).item_len()
        
        for i in self.G_2:
            if i.item_len() < m:
                i.insert_data(DataGroupItem(-1,-1,m-i.item_len()))

    def has_data_group_member(self, data_group_member, level):
        for line in self.G_2:
            if line.has_data(data_group_member, level):
                return True
        return False

    def access_time(self, data_group_member, level, start_time):

        members = len(self.G_2)

        temp_time = [0 for x in range(0, members)]

        for line in range(0, members):
            if self.G_2[line].has_data(data_group_member, level):
                temp_time[line] = self.G_2[line].line_access_time(data_group_member, \
                                                            level, start_time)

        return max(temp_time)

    

class ChannelGroup(object):

    def __init__(self, num, G_3 = None):

        self.num = num
        self.G_3 = []

        for i in range(1, GlobalVar.T + 1):
            self.G_3.append(ChannelGroupMember(self.num,(i-1)*self.num+1))

    def print_groups(self):
        for i in range(1, GlobalVar.T + 1):
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
        for i in range(1, GlobalVar.T + 1):
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

    def target_channel_length(self, data_group_member, level):
        for member in self.G_3:
            if member.has_data_group_member(data_group_member, level):
                return member.member_len()

    def access_target(self, data_group_member, level, start_time):
        for member in self.G_3:
            if member.has_data_group_member(data_group_member, level):
                return member.access_time(data_group_member, level, start_time)
