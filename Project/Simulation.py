from SimAlgoImplement import set_param
from PerformEval import average_criterion, avg_access_time, access_time_criterion, zipf_criterion
from DivideData import divide_video
from SimOutput import output_graph

def main():

    '''
        Set the parameters
        N_1:    No. of the channels in the system
        P_1:    No. of the data group members in a program
        K_1:    No. of quality requirements
        U_1:    Channel constraint for one client
        In_1:   Length of the index
        rate_1: Transformation bit rate
        rate_2: User download bit rate
    '''

    #set_param(10, 500, 3, 5, 1, 5120, 262144)

    #divide_video()

    #average_criterion(10)

    #access_time_criterion(50, 600)

    #zipf_criterion(50, 600)

    #output_graph()

if __name__ == '__main__':
    main()
    

        

