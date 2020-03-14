import matplotlib.pyplot as plt
import csv
from operator import itemgetter

def read_to_array(file_name, array):
    with open(file_name) as file:
        reader = csv.reader(file)
        for row in reader:
            array.append(tuple(map(lambda x : float(x), row)))


def plot_comparison(x_legend, y_legend, x_values,array):
    fig = plt.figure()
    plt.scatter(x_values, map(lambda x: x[0],array),color='b',marker='+', label='REF')
    plt.scatter(x_values, map(lambda x: x[2],array), color='k',marker='<', label='SFC-ST')
    plt.scatter(x_values, map(lambda x: x[1],array), color='r',marker='x', label='SFC-TPL')
   # plt.axhline(0, color='black')
    plt.ylim(ymin=0)
    plt.xlabel(x_legend)
    plt.ylabel(y_legend)
    plt.legend()
    plt.show()

def main():
    deviation = []
    delay = []
    load = []
    x_values = range(1000)

    # read from csv file to array of 3-tuples (REF,TPL,ST)
    read_to_array("deviation_sum_1000.csv", deviation)
    read_to_array("delay_sum_1000.csv", delay)
    read_to_array("network_load_1000.csv", load)

    # sort after reference
    deviation_sorted = sorted(deviation,key=lambda x:x[0])
    delay_sorted = sorted(delay,key=lambda x:x[0])
    load_sorted = sorted(load,key=lambda x:x[0])

    tpl_better_ref = 0
    tpl_worse_ref = 0
    tpl_equal_ref = 0
    st_better_ref = 0
    st_worse_ref = 0
    st_equal_ref = 0
    st_better_tpl = 0
    st_worse_tpl = 0
    st_equal_tpl = 0

    for ref,tpl,st in deviation_sorted:
        if tpl < ref:
            tpl_better_ref +=1
        elif tpl > ref:
            tpl_worse_ref +=1
        else:
            tpl_equal_ref +=1

        if st < ref:
            st_better_ref +=1
        elif st > ref:
            st_worse_ref +=1
        else:
            st_equal_ref +=1

        if st < tpl:
            st_better_tpl +=1
        elif st > tpl:
            st_worse_tpl +=1
        else: 
            st_equal_tpl +=1

    #print("tpl_better_ref: %s" % tpl_better_ref)
    #print("tpl_worse_ref: %s" % tpl_worse_ref)
    #print("tpl_equal_ref: %s" % tpl_equal_ref)

    #print("st_better_ref: %s" % st_better_ref)
    #print("st_worse_ref: %s" % st_worse_ref)
    #print("st_equal_ref: %s" % st_equal_ref)
    print("deviation")
    print("st_better_tpl: %s" % st_better_tpl)
    print("st_worse_tpl: %s" % st_worse_tpl)
    print("st_equal_tpl: %s" % st_equal_tpl)

    tpl_better_ref = 0
    tpl_worse_ref = 0
    tpl_equal_ref = 0
    st_better_ref = 0
    st_worse_ref = 0
    st_equal_ref = 0
    st_better_tpl = 0
    st_worse_tpl = 0
    st_equal_tpl = 0

    for ref,tpl,st in delay_sorted:
        if tpl < ref:
            tpl_better_ref +=1
        elif tpl > ref:
            tpl_worse_ref +=1
        else:
            tpl_equal_ref +=1

        if st < ref:
            st_better_ref +=1
        elif st > ref:
            st_worse_ref +=1
        else:
            st_equal_ref +=1

        if st < tpl:
            st_better_tpl +=1
        elif st > tpl:
            st_worse_tpl +=1
        else: 
            st_equal_tpl +=1

    print("delay")
    print("st_better_tpl: %s" % st_better_tpl)
    print("st_worse_tpl: %s" % st_worse_tpl)
    print("st_equal_tpl: %s" % st_equal_tpl)

    tpl_better_ref = 0
    tpl_worse_ref = 0
    tpl_equal_ref = 0
    st_better_ref = 0
    st_worse_ref = 0
    st_equal_ref = 0
    st_better_tpl = 0
    st_worse_tpl = 0
    st_equal_tpl = 0

    for ref,tpl,st in load_sorted:
        if tpl < ref:
            tpl_better_ref +=1
        elif tpl > ref:
            tpl_worse_ref +=1
        else:
            tpl_equal_ref +=1

        if st < ref:
            st_better_ref +=1
        elif st > ref:
            st_worse_ref +=1
        else:
            st_equal_ref +=1

        if st < tpl:
            st_better_tpl +=1
        elif st > tpl:
            st_worse_tpl +=1
        else: 
            st_equal_tpl +=1

    print("load")
    print("st_better_tpl: %s" % st_better_tpl)
    print("st_worse_tpl: %s" % st_worse_tpl)
    print("st_equal_tpl: %s" % st_equal_tpl)

    # plot
    plot_comparison('experiment number after sorting', 'sum of delay deviations' , x_values, deviation_sorted)
    plot_comparison('experiment number after sorting', 'sum of maximum delays' , x_values, delay_sorted)
    plot_comparison('experiment number after sorting', 'network load' , x_values, load_sorted)

if __name__ == '__main__':
    main()

