import GlobalVar
import random
from SimAlgoImplement import select_func, generate_data_groups
from SimOutput import output_file
import json
import numpy

'''
    Run the 8 algorithms for 'iters' times each, using the same data group

    Results: 
        0. average makespan  
        1. average channel length
        2. average unused channel length
        3. percentage of average unused channel length
'''

def average_criterion(iters):

    ChannelLength = [
        [0 for index in range(0, 8)],
        [0 for index in range(0, 8)],
        [0 for index in range(0, 8)],
        [0 for index in range(0, 8)]
    ]

    proceed = 0

    for times in range(0, iters):

        proceed += 1

        print 'iter: %d/%d' %(proceed, iters)

        Groups = generate_data_groups(False)

        for index in range(0, 8):
            CG = select_func(index, 0, Groups)
            ChannelLength[0][index] += CG.get_maxlen()
            ChannelLength[1][index] += CG.get_totallen()/GlobalVar.N
            ChannelLength[2][index] += CG.get_holelen()
            ChannelLength[3][index] += CG.get_holelen() * 100/float(CG.get_totallen())
            

    
    for index in range(0, 8):
        ChannelLength[0][index] /= iters
        ChannelLength[1][index] /= iters
        ChannelLength[2][index] /= iters
        ChannelLength[3][index] /= iters


    print '\nAverage makespan for iteration %d:' %iters
    output_stream = json.dumps(ChannelLength[0])
    output_file("Average_Criterion_0_%diters_%dN_%dP_%dK_%dU" %(iters,\
                GlobalVar.N, GlobalVar.P, GlobalVar.K, GlobalVar.U), output_stream)

    print '''SDAA:\t\t%d\nISDAA:\t\t%d
        \nSDAA-MDAA:\t%d\nISDAA-MDAA:\t%d
        \nSDAA-AEA:\t%d\nISDAA-AEA:\t%d
        \nSDAA-COA:\t%d\nISDAA-COA:\t%d''' %(tuple(ChannelLength[0]))

    print '\nAverage channel length for iteration %d:' %iters
    output_stream = json.dumps(ChannelLength[1])
    output_file("Average_Criterion_1_%diters_%dN_%dP_%dK_%dU" %(iters,\
                GlobalVar.N, GlobalVar.P, GlobalVar.K, GlobalVar.U), output_stream)

    print '''SDAA:\t\t%d\nISDAA:\t\t%d
        \nSDAA-MDAA:\t%d\nISDAA-MDAA:\t%d
        \nSDAA-AEA:\t%d\nISDAA-AEA:\t%d
        \nSDAA-COA:\t%d\nISDAA-COA:\t%d''' %(tuple(ChannelLength[1]))

    print '\nAverage unused channel length for iteration %d:' %iters
    output_stream = json.dumps(ChannelLength[2])
    output_file("Average_Criterion_2_%diters_%dN_%dP_%dK_%dU" %(iters,\
                GlobalVar.N, GlobalVar.P, GlobalVar.K, GlobalVar.U), output_stream)

    print '''SDAA:\t\t%d\nISDAA:\t\t%d
        \nSDAA-MDAA:\t%d\nISDAA-MDAA:\t%d
        \nSDAA-AEA:\t%d\nISDAA-AEA:\t%d
        \nSDAA-COA:\t%d\nISDAA-COA:\t%d''' %(tuple(ChannelLength[2]))


    print '\nAverage percentage of unused channel length for iteration %d:' %iters
    output_stream = json.dumps(ChannelLength[3])
    output_file("Average_Criterion_3_%diters_%dN_%dP_%dK_%dU" %(iters,\
                GlobalVar.N, GlobalVar.P, GlobalVar.K, GlobalVar.U), output_stream)
    print '''SDAA:\t\t%.4f%%\nISDAA:\t\t%.4f%%
        \nSDAA-MDAA:\t%.4f%%\nISDAA-MDAA:\t%.4f%%
        \nSDAA-AEA:\t%.4f%%\nISDAA-AEA:\t%.4f%%
        \nSDAA-COA:\t%.4f%%\nISDAA-COA:\t%.4f%%''' %(tuple(ChannelLength[3]))


'''
    Simulate 'users' users to access the broadcasting system

    Each user will request for a certain piece of data 
    ('channel_group' -> 'data_group_member' -> 'level')

    Calculate the average access time for these users
'''

def avg_access_time(channel_group, data_group_member, level, users):

    access_time = 0

    for time in range(0, users):
        start = random.randint(0, \
            channel_group.target_channel_length(data_group_member, level) - 1)

        access_time += channel_group.access_target(data_group_member, level, start)

    access_time = access_time / float(users)
    return access_time


'''
    Simulate 'users' users to access the broadcasting system, for 'iters' times

    Each user will ask for a certain piece of data, which means he must download 
    the whole data group member of that data

    In each 'iters', a data group will be generated and then accessed by 'users'

    Calculate the avreage access time of the 'users' when using a 
    certain algorithm
'''

def access_time_criterion(iters, users):

    proceed = 0

    total_avg = [0 for x in range(0, 8)]

    for times in range(0, iters):

        proceed += 1

        print '\niter: %d/%d\n' %(proceed, iters)

        groups = generate_data_groups(False)

        target_member = random.randint(1, GlobalVar.P)

        target_level = random.randint(1, GlobalVar.K)

        for index in range(0, 8):
            print 'processing: algo %d' %(index)
            channel_group = select_func(index, 0, groups)
            total_avg[index] += avg_access_time(channel_group, \
                target_member, target_level, users)

    total_avg = [(x / float(iters)) * 8 / GlobalVar.DOWNLOAD_RATE for x in total_avg]
            
    output_stream = json.dumps(total_avg)
    output_file("Access_Time_%diters_%dusers_%dN_%dP_%dK_%dU" %(iters, users,\
                GlobalVar.N, GlobalVar.P, GlobalVar.K, GlobalVar.U), output_stream)

    print '''\nAverage access time  for %d times, %d users:''' %(iters, users)
    print '''SDAA:%.2f\nISDAA:%.2f
    \nSDAA-MDAA:%.2f\nISDAA-MDAA:%.2f
    \nSDAA-AEA:%.2f\nISDAA-AEA:%.2f
    \nSDAA-COA:%.2f\nISDAA-COA:%.2f''' % (tuple(total_avg))

'''
    Simulate 'users' users to access the broadcasting system, for 'iters' times

    Each user will ask for a certain piece of data, whose popularity is defined by 
    the Zipf's law.

    In each 'iters', a data group will be generated and then accessed by 'users'

    Calculate the avreage access time of the 'users' when using a 
    certain algorithm    
'''

def zipf_criterion(iters, users):

    proceed = 0

    total_avg = [0 for x in range(0, 8)]

    zipf_list = numpy.random.zipf(1.001, iters*100)

    avail_list = 0

    while True:
        index = random.randint(1,300)

        zipf_list_new = [(x + index) for x in zipf_list]

        avail_list = [x for x in zipf_list_new if x <= GlobalVar.P][:(iters+10)]

        if len(avail_list) >= iters:
            break

    for times in range(0, iters):

        proceed += 1

        print '\niter: %d/%d\n' %(proceed, iters)

        groups = generate_data_groups(False)

        target_member = avail_list[proceed]

        target_level = random.randint(1, GlobalVar.K)

        for index in range(0, 8):
            print 'processing: algo %d' %(index)
            channel_group = select_func(index, 0, groups)
            total_avg[index] += avg_access_time(channel_group, \
                target_member, target_level, users)

    total_avg = [(x / float(iters)) * 8 / GlobalVar.DOWNLOAD_RATE for x in total_avg]
            
    output_stream = json.dumps(total_avg)
    output_file("Zipf_Time_%diters_%dusers_%dN_%dP_%dK_%dU" %(iters, users,\
                GlobalVar.N, GlobalVar.P, GlobalVar.K, GlobalVar.U), output_stream)
    print '''\nZipf access time  for %d times, %d users:''' %(iters, users)
    print '''SDAA:%.2f\nISDAA:%.2f
    \nSDAA-MDAA:%.2f\nISDAA-MDAA:%.2f
    \nSDAA-AEA:%.2f\nISDAA-AEA:%.2f
    \nSDAA-COA:%.2f\nISDAA-COA:%.2f''' % (tuple(total_avg))