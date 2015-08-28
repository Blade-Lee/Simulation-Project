import copy


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