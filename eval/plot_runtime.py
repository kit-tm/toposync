import matplotlib.pyplot as plt
import numpy as np
import csv
from plot_experiment import read_to_array
from collections import Counter

def plot(x_legend, y_legend, x_arrays, y_arrays, loc, first_three_labels, second_three_labels):
    assert len(x_arrays) == len(y_arrays)

    color_sequence = ['blue', 'orange', 'green']
    fig = plt.figure()

    for idx, y_array in enumerate(y_arrays):
        label = ""
        if idx < 3:
            label = "%s: VNF count %s" % (first_three_labels, idx)
            print(label)
            print ("x_array %s" % x_arrays[idx])
            print("y_array %s" % y_array)
            for i in range(len(y_array)):
                print str(x_arrays[idx][i]) + ":" + str(y_array[i])

            plt.plot(x_arrays[idx], y_array, label=label, color=color_sequence[idx], linestyle='--')
        else:
            label = "%s: VNF count %s" % (second_three_labels, (idx - 3))
            print(label)
            print ("x_array %s" % x_arrays[idx])
            print("y_array %s" % y_array)
            for i in range(len(y_array)):
                print str(x_arrays[idx][i]) + ":" + str(y_array[i])

            plt.plot(x_arrays[idx], y_array, label=label, color=color_sequence[idx-3], linestyle='-')

    plt.xlabel(x_legend)
    plt.ylabel(y_legend)
    plt.legend(loc=loc, handlelength=3)
    plt.title("n=1000 experiments per VNF count")
    plt.xlim(xmin=0, xmax=max(map(lambda x: x[len(x)-1], x_arrays)))
    plt.ylim(ymin=-0.05)

    plt.show()

def plot2(x_legend, y_legend, x_arrays, y_arrays, loc):
    assert len(x_arrays) == len(y_arrays)

    plt.rcParams.update({'font.size': 16})

    color_sequence = ['blue', 'orange', 'green']

    label = ['TopoSync-SFC: VNF count = ']

    fig = plt.figure()

    for idx, y_array in enumerate(y_arrays):
        if True:
            #print ("x_array %s" % x_arrays[idx])
            #print("y_array %s" % y_array)
            for i in range(len(y_array)):
                if y_array[i] != 1.0 and y_array[i] != 0.0:
                    print str(x_arrays[idx][i]) + ":" + str(y_array[i])
            label = 'TopoSync-SFC: VNF count=%s' % idx
            if idx == 0:
                label = 'TopoSync [1]'
            plt.plot(x_arrays[idx], y_array, color=color_sequence[idx], label=label)

    plt.xlabel(x_legend)
    plt.ylabel(y_legend)
    plt.title("n=1000 experiments per VNF count", fontdict={'fontsize' : 16})
    plt.legend(prop={'size': 13})
    plt.xticks([0, 10000, 20000, 30000, 40000, 50000], map(lambda x: int(x/1000), [0, 10000, 20000, 30000, 40000, 50000]))
    plt.xlim(xmin=0, xmax=max(map(lambda x: x[len(x)-1], x_arrays)))
    plt.xlim(xmin=0, xmax=56507)
    plt.ylim(ymin=-0.05)
    plt.savefig('runtime.png',bbox_inches='tight')
    #plt.show()
    plt.autoscale()


def get_splitted_arrays_for_vnf_cases(array):
    #Splits the csv array to seperate the VNF cases. 
    #example: [[1,1,1],[2,2,2],[3,3,3],[4,4,4],[5,5,5],[6,6,6]] => [ [[1,1,1],[4,4,4]], [[2,2,2],[5,5,5]], [[3,3,3],[6,6,6]] ]
    splitted = []
    for i in range(3):
        splitted.append([array[x] for x in range(0,len(array)) if (x % 3 == i)])
    return splitted

def arr_to_cdf_arr(diff_arr):
    cdf_arr = sorted(map(lambda x : (x[0], x[1] / 1000.0), Counter(diff_arr).iteritems()), key= lambda x : x[0])
    propability_sum = 0
    for idx, i in enumerate(cdf_arr):
        propability_sum += i[1]
        cdf_arr[idx] = (i[0], propability_sum)
        #print cdf_arr[idx]
    return cdf_arr

runtimes = []
read_to_array("data/runtimes/runtime.csv", runtimes)
runtimes_splitted = get_splitted_arrays_for_vnf_cases(runtimes)
runtimes_tpl_0 = map(lambda x: x[0], runtimes_splitted[0])
runtimes_tpl_1 = map(lambda x: x[0], runtimes_splitted[1])
runtimes_tpl_2 = map(lambda x: x[0], runtimes_splitted[2])

cdf_tpl_0 = arr_to_cdf_arr(runtimes_tpl_0)
pad = range(0, 207)
pad.reverse()
for i in pad:
    cdf_tpl_0.insert(0, (i, 0))
for i in range(2844,56507):
    cdf_tpl_0.append((i, 1.0))
cdf_tpl_1 = arr_to_cdf_arr(runtimes_tpl_1)
pad = range(0, 491)
pad.reverse()
for i in pad:
    cdf_tpl_1.insert(0, (i, 0))
for i in range(3934,56507):
    cdf_tpl_1.append((i, 1.0))
cdf_tpl_2 = arr_to_cdf_arr(runtimes_tpl_2)
pad = range(0, 777)
pad.reverse()
for i in pad:
    cdf_tpl_2.insert(0, (i, 0))

runtimes_st_0 = map(lambda x: x[1], runtimes_splitted[0])
runtimes_st_1 = map(lambda x: x[1], runtimes_splitted[1])
runtimes_st_2 = map(lambda x: x[1], runtimes_splitted[2])
cdf_st_0 = arr_to_cdf_arr(runtimes_st_0)
pad = range(0, 69)
pad.reverse()
for i in pad:
    cdf_st_0.insert(0, (i, 0))
for i in range(176,1214):
    cdf_st_0.append((i, 1.0))
cdf_st_1 = arr_to_cdf_arr(runtimes_st_1)
pad = range(0, 153)
pad.reverse()
for i in pad:
    cdf_st_1.insert(0, (i, 0))
for i in range(772,1214):
    cdf_st_1.append((i, 1.0))
cdf_st_2 = arr_to_cdf_arr(runtimes_st_2)
pad = range(0, 236)
pad.reverse()
for i in pad:
    cdf_st_2.insert(0, (i, 0))

#x_arrs = [map(lambda x: x[0], cdf_tpl_0), map(lambda x: x[0], cdf_tpl_1), map(lambda x: x[0], cdf_tpl_2), map(lambda x: x[0], cdf_st_0), map(lambda x: x[0], cdf_st_1), map(lambda x: x[0], cdf_st_2)]
#y_arrs = [map(lambda x: x[1], cdf_tpl_0), map(lambda x: x[1], cdf_tpl_1), map(lambda x: x[1], cdf_tpl_2), map(lambda x: x[1], cdf_st_0), map(lambda x: x[1], cdf_st_1), map(lambda x: x[1], cdf_st_2)]

#plot("runtime [in ms]", "cumulative probability", x_arrs, y_arrs, "best", "SFC-TPL", "SFC-ST")

x_arrs = [map(lambda x: x[0], cdf_tpl_0), map(lambda x: x[0], cdf_tpl_1), map(lambda x: x[0], cdf_tpl_2)]
y_arrs = [map(lambda x: x[1], cdf_tpl_0), map(lambda x: x[1], cdf_tpl_1), map(lambda x: x[1], cdf_tpl_2)]

plot2("runtime [in s]", "cumulative probability", x_arrs, y_arrs, "best")



