from SimAlgoImplement import set_param
from PerformEval import average_criterion, avg_access_time, access_time_criterion


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

    #average_criterion(3, 20)

    access_time_criterion(50, 1000)

if __name__ == '__main__':
    main()
    

        

