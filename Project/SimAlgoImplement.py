import GlobalVar
from SimAlgo import SDAA, AEA, COA, MDAA, ISDAA
from DataGroup import DataGroup
from SimDebugTool import data_checker
import copy

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

    for i in range(0, GlobalVar.P):

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

    select = func_list[num]

    Group = 0
    limit = 0

    if select[1] == None:
        limit = GlobalVar.K
        Group = G[0]
    else:
        limit = GlobalVar.U
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

    GlobalVar.N = N_1
    GlobalVar.P = P_1
    GlobalVar.K = K_1
    GlobalVar.U = U_1
    GlobalVar.In = In_1
    GlobalVar.mu = mu_1
    GlobalVar.sig = sig_1