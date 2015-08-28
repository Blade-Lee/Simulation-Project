import GlobalVar
import random
from SimAlgoImplement import select_func, generate_data_groups

'''
    Run the 8 algorithms for 'iter' times each, using the same data group

    'option': 
        0. average makespan  
        1. average channel length
        2. average unused channel length
        3. percentage of average unused channel length
'''

def average_criterion(option, iter):

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
                ChannelLength[index] += CG.get_totallen()/GlobalVar.N
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


def avg_access_time(channel_group, data_group_member, level, users):

    access_time = 0

    for time in range(0, users):
        start = random.randint(0, \
            channel_group.target_channel_length(data_group_member, level) - 1)

        access_time += channel_group.access_target(data_group_member, level, start)

    access_time = access_time / float(users)
    return access_time


'''
    Simulate 'users' users to access the broadcasting system, for 'iter' times

    Each user will ask for a certain piece of data, which means he must download 
    the whole data group member of that data

    In each 'iter', a data group will be generated and then accessed by 'users'

    Calculate the avreage access time of the 'users' when using a 
    certain algorithm
'''

def access_time_criterion(iter, users):

    access_time = [[0 for index in range(0, 8)] for index in range(0, GlobalVar.K)]

    proceed = 0

    total_avg = [0 for x in range(0, 8)]

    for times in range(0, iter):

        proceed += 1

        if proceed * 100 / iter % 5 == 0:
            print 'Proceed: %d%%' %(proceed * 100 / iter)

        groups = generate_data_groups(False)

        target_member = random.randint(1, GlobalVar.P)

        target_level = random.randint(1, GlobalVar.K)

        for index in range(0, 8):
            channel_group = select_func(index, 0, groups)
            total_avg[index] += avg_access_time(channel_group, \
                target_member, target_level, users)

    total_avg = [x/float(iter) for x in total_avg]
            

    print '''\nAverage access time on data %d and level %d for %d times, %d users:''' \
        %(target_member, target_level, iter, users)
    print '''SDAA:%.2f\nISDAA:%.2f
    \nSDAA-MDAA:%.2f\nISDAA-MDAA:%.2f
    \nSDAA-AEA:%.2f\nISDAA-AEA:%.2f
    \nSDAA-COA:%.2f\nISDAA-COA:%.2f''' % (tuple(total_avg))