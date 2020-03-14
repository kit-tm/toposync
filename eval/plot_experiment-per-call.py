import matplotlib.pyplot as plt
import numpy as np
import csv
from plot_experiment import read_to_array

deviation = []
delay = []
load = []
x_values = range(100)


def plot_comparison(x_legend, y_legend, arrays, indices, title ,legend_loc):
    fig = plt.figure()
    if title is not None:
        plt.title(title)

    #plt.scatter(x_values, arrays[0], label='REF-SFC-TPL', marker='+')
    #plt.scatter(x_values, arrays[1], label='REF-SFC-ST', marker='x')

    plt.scatter(x_values, map(lambda x: x[indices[0]],arrays[0]), s=40,color='b',marker='+', label='REF')
    #plt.scatter(x_values, map(lambda x: x[indices[2]],array), s=10,color='orange',marker='x', label='SFC-ST')
    plt.scatter(x_values, map(lambda x: x[indices[1]],arrays[0]), s=10,color='r',marker='x', label='SFC-TPL')
    #plt.ylim(ymin=-5)
    plt.xlabel(x_legend)
    plt.ylabel(y_legend)
    plt.legend(loc=legend_loc)
    plt.show()

def plot_bars():
    width = 0.3
    x = np.arange(3)

    # load, deviation, delay
    tpl_worse = [0,0,0]
    tpl_equal = [0,0,0]
    tpl_better = [0,0,0]

    for ref,tpl,st in load:
        if ref == tpl:
            tpl_equal[0] += 1
        elif ref > tpl:
            tpl_better[0] += 1
        else: 
            tpl_worse[0] += 1

    for ref,_,_,_,tpl,_,_,_,st,_,_,_ in deviation:
        if ref == tpl:
            tpl_equal[1] += 1
        elif ref > tpl:
            tpl_better[1] += 1
        else: 
            tpl_worse[1] += 1

    for ref,_,_,_,tpl,_,_,_,st,_,_,_ in delay:
        if ref == tpl:
            tpl_equal[2] += 1
        elif ref > tpl:
            tpl_better[2] += 1
        else: 
            tpl_worse[2] += 1

    fig = plt.figure()
    ax = plt.subplot(111)

    plt.bar(x,tpl_worse,width,label='SFC-TPL is worse than REF',color='r')
    plt.bar(x + width,tpl_equal,width,label='SFC-TPL is equally good as REF',color='orange')
    plt.bar(x + 2*width,tpl_better,width,label='SFC-TPL is better than REF',color='green')

    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width, box.height * 0.9])

    for a,b in zip(x,tpl_worse):
        plt.text(a - 0.06,b,str(b))

    for a,b in zip(x+width,tpl_equal):
        plt.text(a - 0.06,b,str(b))

    for a,b in zip(x+2*width,tpl_better):
        plt.text(a - 0.06,b,str(b))

    plt.xticks(map(lambda y:y+width,x), ('network load', 'delay deviation sum', 'maximum delay sum'))
    plt.ylabel("amount of experiments")
    plt.legend(loc='center left', bbox_to_anchor=(0, 1.15), ncol=1)
    plt.show()


# read from csv file to array of 3-tuples (REF,TPL,ST)
read_to_array("deviation_sum_new_ref.csv", deviation)
read_to_array("delay_sum_new_ref.csv", delay)
read_to_array("network_load_new_ref.csv", load)


deviation_diff_arr_tpl_ref = []
for ref,_,_,_,tpl,_,_,_,_,_,_,_ in deviation:
    deviation_diff_arr_tpl_ref.append(tpl-ref)
    print(tpl-ref)

delay_diff_arr_tpl_ref = []
for ref,_,_,_,tpl,_,_,_,_,_,_,_ in delay:
    delay_diff_arr_tpl_ref.append(tpl-ref)
    print(tpl-ref)

load_diff_arr_tpl_ref = []
for ref,tpl,_ in load:
    load_diff_arr_tpl_ref.append(tpl-ref)
    print(tpl-ref)

deviation_diff_arr_st_ref = []
for ref,_,_,_,tpl,_,_,_,st,_,_,_ in deviation:
    deviation_diff_arr_st_ref.append(st-ref)

delay_diff_arr_st_ref = []
for ref,_,_,_,tpl,_,_,_,st,_,_,_ in delay:
    delay_diff_arr_st_ref.append(st-ref)

load_diff_arr_st_ref = []
for ref,tpl,st in load:
    load_diff_arr_st_ref.append(st-ref)


#plot_comparison('lel', 'lul',[sorted(deviation_diff_arr_tpl_ref),sorted(deviation_diff_arr_st_ref)],None, 'deviation', 'best')
#plot_comparison('lel', 'lul',[sorted(load_diff_arr_tpl_ref),sorted(load_diff_arr_st_ref)],None, 'load', 'best')
#plot_comparison('lel', 'lul',[sorted(delay_diff_arr_tpl_ref),sorted(delay_diff_arr_st_ref)],None, 'delay', 'best')

load_sorted = sorted(load,key=lambda x:x[0])
#plot_comparison('experiment number after sorting', 'network load' , load_sorted, [0,1,2], None, "lower left")

deviation_sorted = sorted(deviation,key=lambda x:x[0])
#plot_comparison('experiment number after sorting', 'delay deviation sum' , deviation_sorted, [0,4,8], None, "best")
#deviation_sorted = sorted(deviation,key=lambda x:x[1])
#plot_comparison('experiment number after sorting', 'delay deviation' , deviation_sorted, [1,5,9], 'call 1', "best")
#deviation_sorted = sorted(deviation,key=lambda x:x[2])
#plot_comparison('experiment number after sorting', 'delay deviation' , deviation_sorted, [2,6,10], 'call 2', "best")
#deviation_sorted = sorted(deviation,key=lambda x:x[3])
#plot_comparison('experiment number after sorting', 'delay deviation' , deviation_sorted, [3,7,11], 'call 3', "best")

delay_sorted = sorted(delay,key=lambda x:x[0])
#plot_comparison('experiment number after sorting', 'max delay sum' , delay_sorted, [0,4,8], None, "lower left")
#delay_sorted = sorted(delay,key=lambda x:x[1])
#plot_comparison('experiment number after sorting', 'max delay' , delay_sorted, [1,5,9], 'call 1', "best")
#delay_sorted = sorted(delay,key=lambda x:x[2])
#plot_comparison('experiment number after sorting', 'max delay' , delay_sorted, [2,6,10], 'call 2', "best")
#delay_sorted = sorted(delay,key=lambda x:x[3])
#plot_comparison('experiment number after sorting', 'max delay' , delay_sorted, [3,7,11], 'call 3', "best")

plot_comparison('lel', 'lul',[deviation_sorted],[0,4,8], 'deviation', 'best')
plot_comparison('lel', 'lul',[load_sorted],[0,1,2], 'load', 'best')
plot_comparison('lel', 'lul',[delay_sorted],[0,4,8], 'delay', 'best')