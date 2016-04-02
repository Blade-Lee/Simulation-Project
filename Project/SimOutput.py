import os, sys
import json
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1.axes_divider import make_axes_area_auto_adjustable

def output_file(file_name, file_stream):
    file_path = os.path.join(sys.path[0], "..\output\\" + file_name + ".txt")

    with open(file_path, "w") as output_stream:
        output_stream.write(file_stream)

def output_graph():

    data_path = os.path.join(sys.path[0], "..\output")
    current_list = os.listdir(data_path)
    
    avg_total = [[-1 for y in range(4)] for x in range(6)]
    access_total = [-1 for x in range(3)]
    zipf_total = [-1 for x in range(3)]

    for each_file in current_list:
        if ".txt" in each_file:
            temp_json = 0

            with open(os.path.join(data_path, each_file), "r") as temp_file:
                temp_json = json.load(temp_file)
            
            new_file_name = each_file.split(".")[0]
            file_names = new_file_name.split("_")
            
            if file_names[0] == "Average":
                if file_names[6] == "4K":
                    if file_names[5] == "500P":
                        avg_total[0][int(file_names[2])] = temp_json
                    else:
                        avg_total[1][int(file_names[2])] = temp_json

                if file_names[6] == "3K":
                    if file_names[5] == "500P":
                        avg_total[2][int(file_names[2])] = temp_json
                    else:
                        avg_total[3][int(file_names[2])] = temp_json

                if file_names[6] == "2K":
                    if file_names[5] == "500P":
                        avg_total[4][int(file_names[2])] = temp_json
                    else:
                        avg_total[5][int(file_names[2])] = temp_json

            if file_names[0] == "Access":
                if file_names[3] == "200users":
                    access_total[0] = temp_json
                if file_names[3] == "400users":
                    access_total[1] = temp_json
                if file_names[3] == "600users":
                    access_total[2] = temp_json

            if file_names[0] == "Zipf":
                if file_names[3] == "200users":
                    zipf_total[0] = temp_json
                if file_names[3] == "400users":
                    zipf_total[1] = temp_json
                if file_names[3] == "600users":
                    zipf_total[2] = temp_json

    x_axis = [x for x in range(1,9)]

    '''
    count = 0

    for group in avg_total:

        if count == 5:

            fig = plt.figure(figsize=(8,8), dpi=75)

            ax1 = fig.add_subplot(111)
            ax1.bar([x-0.4 for x in x_axis], group[3], facecolor='#9a9a9a', alpha=0.7, edgecolor='white', label=r'$Avg_3$')
            ax1.set_ylabel(r'percentage for $Avg_3$', fontsize=18)
            ax1.set_yticks([x for x in range(0,45,10)])
            ax1.set_yticklabels([r'$0\%$', r'$10\%$', r'$20\%$', r'$30\%$', \
                    r'$40\%$', r'$50\%$', r'$60\%$', r'$70\%$', r'$80\%$', r'$90\%$'])
            ax1.set_xticks(x_axis)
            ax1.set_xticklabels([r'$SDAA$', r'$ISDAA$', r'$SDAA-MDAA$', r'$ISDAA-MDAA$', r'$SDAA-AEA$', \
                    r'$ISDAA-AEA$', r'$SDAA-COA$', r'$ISDAA-COA$'], rotation=-45, ha="left", fontsize=14)
            ax1.set_xlim(0, 9)
            ax1.grid(color='grey', alpha=0.5, linestyle='--', linewidth=0.2)

            ax2 = ax1.twinx()
            ax2.plot(x_axis, group[0], linewidth=4, color="#000000", alpha=1, linestyle="-", label=r'$Avg_0$')
            ax2.plot(x_axis, group[1], linewidth=4, color="#ff0000", alpha=1, linestyle="--", label=r'$Avg_1$')
            ax2.plot(x_axis, group[2], linewidth=4, color="#ff0000", alpha=1, linestyle="-", label=r'$Avg_2$')
            ax2.set_yticks([x for x in range(0, 160000000, 25000000)])
            ax2.set_yticklabels([r'$0.0$', r'$0.25$', r'$0.5$', r'$0.75$', r'$1.0$', r'$1.25$', r'$1.5$', r'$1.75$', r'$2.0$'])
            ax2.set_ylabel(r'size ($\times10^8$ Bytes)', fontsize=18)
            ax2.set_xlim(0, 9)

            handles, labels = ax1.get_legend_handles_labels()
            handles_temp, labels_temp = ax2.get_legend_handles_labels()

            handles_temp.append(handles[0])
            labels_temp.append(labels[0])

            ax2.legend(handles_temp, labels_temp, fontsize=18)

            plt.show()

        count += 1
    '''

    fig = plt.figure(figsize=(8,8), dpi=75)

    ax1 = fig.add_subplot(111)
    ax1.grid(color='grey', alpha=0.5, linestyle='--', linewidth=0.2)
    ax1.set_xlim(-1, 17)

    ax1.bar([x-0.75 for x in np.arange(1, 16, 2)], zipf_total[0], 0.5, facecolor='#9a9a9a', alpha=1, \
            edgecolor='white', label='users='+r'$200$')
    ax1.bar([x-0.25 for x in np.arange(1, 16, 2)], zipf_total[1], 0.5, facecolor='#000000', alpha=1, \
            edgecolor='white', label='users='+r'$400$')
    ax1.bar([x+0.25 for x in np.arange(1, 16, 2)], zipf_total[2], 0.5, facecolor='#ff0000', alpha=1, \
            edgecolor='white', label='users='+r'$600$')

    ax1.set_ylabel('Time '+r'($seconds$)', fontsize=18)
    ax1.set_yticks([x for x in range(0,560,50)])
    ax1.set_yticklabels([r'$0$', r'$50$', r'$100$', r'$150$', \
            r'$200$', r'$250$', r'$300$', r'$350$', r'$400$', r'$450$', r'$500$', r'$550$'])

    ax1.set_xticks([x for x in range(1, 16, 2)])
    ax1.set_xticklabels([r'$SDAA$', r'$ISDAA$', r'$SDAA-MDAA$', r'$ISDAA-MDAA$', r'$SDAA-AEA$', \
                    r'$ISDAA-AEA$', r'$SDAA-COA$', r'$ISDAA-COA$'], rotation=-45, ha="left", fontsize=14)

    handles, labels = ax1.get_legend_handles_labels()

    ax1.legend(handles, labels, fontsize=18)

    plt.show()



