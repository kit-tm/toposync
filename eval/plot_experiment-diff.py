import matplotlib.pyplot as plt
import numpy as np
import csv
from plot_experiment import read_to_array
import matplotlib.ticker as mtick
from collections import Counter

def plot(x_legend, y_legend, x_arrays, y_arrays, title, loc, first_three_labels, second_three_labels, is_tpl_st=False, is_load=False, x_ticks_steps=None):
    assert len(x_arrays) == len(y_arrays)
    #assert len(x_arrays) == 6

    plt.rcParams.update({'font.size': 22})

    color_sequence = ['blue', 'orange', 'green']
    marker_sequence = ['o', "s", "D"]


    fig = plt.figure()
    if title is not None:
        plt.title(title, fontdict={'fontsize' : 24})
    for idx, y_array in enumerate(y_arrays):
        if is_tpl_st:
            if idx == 0:
                plt.plot(x_arrays[idx], y_array, label="SFC-ST + SFC-TPL: VNF count 0", color='blue', linestyle='-.',marker='o',markersize=5)
                continue

            if idx == 3:
                continue

        # higlight for presentation
        #if x_legend == "delay_deviation [in link delays]" and first_three_labels == "REF" and second_three_labels == "SFC-TPL" and idx not in [2,5]:
        #    print str(idx) + "continueing"
        #    continue

        label = ""
        if idx < 3:
            label = "%s: VNF count=%s" % (first_three_labels, idx)
            print(label)
            print ("x_array %s" % x_arrays[idx])
            print("y_array %s" % y_array)
            for i in range(len(y_array)):
                print(str(x_arrays[idx][i]) + ":" + str(y_array[i]))

            plt.plot(x_arrays[idx], y_array, label=label, color=color_sequence[idx], linestyle='--')#,marker=marker_sequence[idx],markersize=3)
        else:
            label = "%s: VNF count=%s" % (second_three_labels, (idx - 3))
            if idx == 3:
                label = "TopoSync [1]"
            print(label)
            print ("x_array %s" % x_arrays[idx])
            print("y_array %s" % y_array)
            for i in range(len(y_array)):
                print(str(x_arrays[idx][i]) + ":" + str(y_array[i]))

            plt.plot(x_arrays[idx], y_array, label=label, color=color_sequence[idx-3], linestyle='-')#,marker=marker_sequence[idx-3],markersize=3)




    plt.xlabel(x_legend)
    plt.ylabel(y_legend)
    plt.legend(loc=loc, handlelength=3, prop={'size': 15})
    print("xmax: %s" % (max(map(lambda x: x[len(x)-1], x_arrays)) / 5))
    plt.xlim(xmin=0, xmax=max(map(lambda x: x[len(x)-1], x_arrays)))
    if is_load:
        plt.xticks(plt.xticks()[0], map(lambda x: int(x/4), plt.xticks()[0]))
    else:
        plt.xticks(plt.xticks()[0], map(lambda x: int(x/5), plt.xticks()[0]))
        #plt.xticks(range(0,max(map(lambda x: x[len(x)-1], x_arrays))+5, 5), map(lambda x: int(x/5), range(0,max(map(lambda x: x[len(x)-1], x_arrays))+5, 5)))
    
    # highlight values for presentation
    #if x_legend == "delay_deviation [in link delays]" and first_three_labels == "REF" and second_three_labels == "SFC-TPL":
        # 2 VNFs val
        #plt.plot([0,5], [0.994,0.994], linestyle=':', color='k')
        #plt.plot([5,5], [-0.05, 0.994], linestyle=':', color='k')
        #plt.plot([0,5], [0.095,0.095], linestyle=':', color='k')
        #plt.yticks([0.994, 0.095])

        # 0 VNFs val
        #plt.yticks([0.713, 0.029])

    plt.xlim(xmin=0, xmax=500)
    plt.ylim(ymin=-0.05)
    plt.xticks(map(lambda x: x * 5, [0,20,40,60,80, 100]), [0,20,40,60,80,100])
    #plt.savefig('deviation.png',bbox_inches='tight')
    plt.savefig('sfc_max_delay.png',bbox_inches='tight')
    plt.show()
    plt.autoscale()

def get_splitted_arrays_for_vnf_cases(array):
    #Splits the csv array to seperate the VNF cases. 
    #example: [[1,1,1],[2,2,2],[3,3,3],[4,4,4],[5,5,5],[6,6,6]] => [ [[1,1,1],[4,4,4]], [[2,2,2],[5,5,5]], [[3,3,3],[6,6,6]] ]
    splitted = []
    for i in range(3):
        splitted.append([array[x] for x in range(0,len(array)) if (x % 3 == i)])
    return splitted

def diff_arr_to_cdf_arr(diff_arr):
    cdf_arr = sorted(map(lambda x : (x[0], x[1] / 1000.0), Counter(diff_arr).iteritems()), key= lambda x : x[0])
    propability_sum = 0
    for idx, i in enumerate(cdf_arr):
        propability_sum += i[1]
        cdf_arr[idx] = (i[0], propability_sum)
        print(cdf_arr[idx])
    return cdf_arr 

def plot2(x_legend, y_legend, x_arrays, y_arrays, title, loc, first_label, second_label, is_tpl_st=False, is_load=False, x_ticks_steps=None):
    assert len(x_arrays) == len(y_arrays)

    plt.rcParams.update({'font.size': 12})

    color_sequence = ['blue', 'orange', 'green']
    marker_sequence = ['o', "s", "D"]


    fig = plt.figure()
    if title is not None:
        plt.title(title)
    for idx, y_array in enumerate(y_arrays):
    
        label = ""
        if idx < 1:
            label = "%s" % first_label
            print(label)
            print ("x_array %s" % x_arrays[idx])
            print("y_array %s" % y_array)
            for i in range(len(y_array)):
                print(str(x_arrays[idx][i]) + ":" + str(y_array[i]))

            plt.plot(x_arrays[idx], y_array, label=label, color=color_sequence[idx], linestyle='--',marker=marker_sequence[idx],markersize=5)
        else:
            label = "%s" % second_label

            print(label)
            print ("x_array %s" % x_arrays[idx])
            print("y_array %s" % y_array)
            for i in range(len(y_array)):
                print (str(x_arrays[idx][i]) + ":" + str(y_array[i]))

            plt.plot(x_arrays[idx], y_array, label=label, color=color_sequence[idx-1], linestyle='-',marker=marker_sequence[idx-3],markersize=5)

    plt.xlabel(x_legend)
    plt.ylabel(y_legend)
    plt.legend(loc=loc, handlelength=3)
    print("xmax: %s" % (max(map(lambda x: x[len(x)-1], x_arrays)) / 5))
    plt.xlim(xmin=0, xmax=max(map(lambda x: x[len(x)-1], x_arrays)))
    if is_load:
        plt.xticks(plt.xticks()[0], map(lambda x: int(x/4), plt.xticks()[0]))
    else:
        plt.xticks(plt.xticks()[0], map(lambda x: int(x/5), plt.xticks()[0]))

    plt.xlim(xmin=0, xmax=max(map(lambda x: x[len(x)-1], x_arrays)))
    plt.ylim(ymin=-0.05)

   # plt.plot([0,5], [0.78,0.78], linestyle=':', color='k')
   # plt.plot([5,5], [-0.05, 0.78], linestyle=':', color='k')
   # plt.plot([0,5], [0.2,0.2], linestyle=':', color='k')
   # plt.yticks([0.2,0.78])
    ax =plt.gca()
    ax.yaxis.set_label_coords(-0.1, 0.5)
    plt.autoscale()
    plt.show()

def plot_deviation_cdf():
    ## DEVIATION: TPL vs REF (direct comparison)
    deviation_ref_0 = map(lambda x: x[0], deviation_splitted[0])
    cdf_dev_ref_0 = diff_arr_to_cdf_arr(deviation_ref_0)
    cdf_dev_ref_0.append((45,1.0))

    deviation_tpl_0 = map(lambda x: x[1], deviation_splitted[0])
    cdf_dev_tpl_0 = diff_arr_to_cdf_arr(deviation_tpl_0)
    cdf_dev_tpl_0.append((40, 1.0))
    cdf_dev_tpl_0.append((45, 1.0))

    deviation_ref_1 = map(lambda x: x[0], deviation_splitted[1])
    cdf_dev_ref_1 = diff_arr_to_cdf_arr(deviation_ref_1)
    cdf_dev_ref_1.append((40,1.0))
    cdf_dev_ref_1.append((45,1.0))

    deviation_tpl_1 = map(lambda x: x[1], deviation_splitted[1])
    cdf_dev_tpl_1 = diff_arr_to_cdf_arr(deviation_tpl_1)
    for i in range(20, 50, 5):
        cdf_dev_tpl_1.append((i, 1.0))

    deviation_ref_2 = map(lambda x: x[0], deviation_splitted[2])
    cdf_dev_ref_2 = diff_arr_to_cdf_arr(deviation_ref_2)
    cdf_dev_ref_2.append((40,1.0))
    cdf_dev_ref_2.append((45,1.0))

    deviation_tpl_2 = map(lambda x: x[1], deviation_splitted[2])
    cdf_dev_tpl_2 = diff_arr_to_cdf_arr(deviation_tpl_2)
    for i in range(10, 50, 5):
        cdf_dev_tpl_2.append((i, 1.0))

    x_arrs = [map(lambda x : x[0], cdf_dev_ref_0) , map(lambda x : x[0], cdf_dev_ref_1), map(lambda x : x[0], cdf_dev_ref_2),map(lambda x : x[0], cdf_dev_tpl_0), map(lambda x : x[0], cdf_dev_tpl_1), map(lambda x : x[0], cdf_dev_tpl_2)]
    y_arrs = [map(lambda x : x[1], cdf_dev_ref_0), map(lambda x : x[1], cdf_dev_ref_1), map(lambda x : x[1], cdf_dev_ref_2), map(lambda x : x[1], cdf_dev_tpl_0), map(lambda x : x[1], cdf_dev_tpl_1), map(lambda x : x[1], cdf_dev_tpl_2)]
    plot("delay deviation [in ms]", "cumulative probability", x_arrs, y_arrs, "n=1000 experiments per VNF count", 'best', 'REF', 'TopoSync-SFC', is_tpl_st=False)
 
def plot_delay_cdf():
    ## DELAY: TPL vs REF (direct comparison)
    delay_ref_0 = map(lambda x: x[0], delay_splitted[0])
    cdf_del_ref_0 = diff_arr_to_cdf_arr(delay_ref_0)
    pad = range(0, 50, 5)
    pad.reverse()
    for i in pad:
        cdf_del_ref_0.insert(0, (i, 0))
    for i in range(85, 500, 5):
        cdf_del_ref_0.append((i, 1))

    delay_ref_1 = map(lambda x: x[0], delay_splitted[1])
    cdf_del_ref_1 = diff_arr_to_cdf_arr(delay_ref_1)
    pad = range(0, 90, 5)
    pad.reverse()
    for i in pad:
        cdf_del_ref_1.insert(0, (i, 0))
    for i in range(210, 500, 5):
        cdf_del_ref_1.append((i, 1))

    delay_ref_2 = map(lambda x: x[0], delay_splitted[2])
    cdf_del_ref_2 = diff_arr_to_cdf_arr(delay_ref_2)
    pad = range(0, 215, 5)
    pad.reverse()
    for i in pad:
        cdf_del_ref_2.insert(0, (i, 0))
    for i in range(215, 540, 5):
        cdf_del_ref_2.append((i, 1))

    delay_tpl_0 = map(lambda x: x[1], delay_splitted[0])
    cdf_del_tpl_0 = diff_arr_to_cdf_arr(delay_tpl_0)
    pad = range(0, 50, 5)
    pad.reverse()
    for i in pad:
        cdf_del_tpl_0.insert(0, (i, 0))
    for i in range(85, 540, 5):
        cdf_del_tpl_0.append((i, 1))

    delay_tpl_1 = map(lambda x: x[1], delay_splitted[1])
    cdf_del_tpl_1 = diff_arr_to_cdf_arr(delay_tpl_1)
    pad = range(0, 90, 5)
    pad.reverse()
    for i in pad:
        cdf_del_tpl_1.insert(0, (i, 0))
    for i in range(210, 540, 5):
        cdf_del_tpl_1.append((i, 1))

    delay_tpl_2 = map(lambda x: x[1], delay_splitted[2])
    cdf_del_tpl_2 = diff_arr_to_cdf_arr(delay_tpl_2)
    pad = range(0, 215, 5)
    pad.reverse()
    for i in pad:
        cdf_del_tpl_2.insert(0, (i, 0))
    for i in range(210, 540, 5):
        cdf_del_tpl_2.append((i, 1))

    x_arrs = [map(lambda x : x[0], cdf_del_ref_0) , map(lambda x : x[0], cdf_del_ref_1), map(lambda x : x[0], cdf_del_ref_2),map(lambda x : x[0], cdf_del_tpl_0), map(lambda x : x[0], cdf_del_tpl_1), map(lambda x : x[0], cdf_del_tpl_2)]
    y_arrs = [map(lambda x : x[1], cdf_del_ref_0), map(lambda x : x[1], cdf_del_ref_1), map(lambda x : x[1], cdf_del_ref_2), map(lambda x : x[1], cdf_del_tpl_0), map(lambda x : x[1], cdf_del_tpl_1), map(lambda x : x[1], cdf_del_tpl_2)]
    plot("max delay [in ms]", "cumulative probability", x_arrs, y_arrs, "n=1000 experiments per VNF count", 'lower right', 'REF', 'TopoSync-SFC', is_tpl_st=False)

deviation = []
delay = []

read_to_array("data/new/delay_sum.csv", delay)
read_to_array("data/new/deviation_sum.csv", deviation)

# [0] = 0 VNFs, [1] = 1 VNF, [2] = 2 VNFs
deviation_splitted = get_splitted_arrays_for_vnf_cases(deviation)
delay_splitted = get_splitted_arrays_for_vnf_cases(delay)

plot_deviation_cdf()
plot_delay_cdf()