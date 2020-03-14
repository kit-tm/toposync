import matplotlib.pyplot as plt
import numpy as np
import csv

X_START = 16
X_END = 5 * 16
X_STEP = 4

def read_to_array(file_name, array):
    with open(file_name) as file:
        reader = csv.reader(file)
        for row in reader:
            array.append(tuple(map(lambda x : x if x == 'i' else float(x), row)))

def get_splitted_after_load_constr(arr):
    splitted = []
    for i in range(len(x_loads)):
        splitted.append(map(lambda x: x[i], arr))

    return splitted

def plot_tradeoff(deviation_data, load_data,):
    plt.rcParams.update({'font.size': 20})
    plt.rcParams.update({'xtick.labelsize': 16})
    #plt.rcParams.update({'ytick.labelsize': 16})
    fig, ax1 = plt.subplots()
        
    dev_clean = map(lambda y: filter(lambda x: x != 'i', y), deviation_data)
    dev_inf = map(lambda y: filter(lambda x: x == 'i', y), deviation_data)
    load_clean = map(lambda y: filter(lambda x: x != 'i', y), load_data)
    load_inf = map(lambda y: filter(lambda x: x == 'i', y), load_data)
    
    ax1.plot(x_loads, map(np.average, map(lambda x: map(lambda y: y/5, x),dev_clean)), label='deviation', color='b', marker='x')
    print map(np.average, map(lambda x: map(lambda y: y/5, x),dev_clean))
    dev_clean = map(lambda x: map(lambda y: int(y/5), x),dev_clean)
    ax1.set_xlabel("network load constraint [in links]")
    ax1.set_ylabel("avg. delay deviation [in ms]", color='b')
    ax1.set_yticks(range(0,3,1))
    ax1.tick_params('y', colors='b')
    #ax1.set_xticklabels(map(lambda x: x/4, ax1.get_xticks().tolist()))
    

    #print list(zip(x_loads, map(np.median, map(lambda x: map(lambda y: y/5, x),dev_clean))))
    #print list(zip(x_loads, map(np.median, map(lambda x: map(lambda y: y/4, x), load_clean))))
    ax2 = ax1.twinx()
    ax2.plot(x_loads, map(np.average, map(lambda x: map(lambda y: y/4, x), load_clean)), label='actual load', color='r', marker='x')
    print map(np.average, map(lambda x: map(lambda y: y/4, x), load_clean))
    ax2.set_ylabel("avg. network load [in links]", color='r')
    ax2.tick_params('y', colors='r')
    plt.xticks(range(8*4, 20*4+4,4), map(lambda x: x/4, range(8*4, 20*4+4,4)))#, map(lambda x: x/4, plt.xticks()[0]))
    plt.title("n=3000 experiments")
    #plt.show()
    plt.savefig('sfc_tradeoff.png',bbox_inches='tight')
    #plt.show()
    plt.autoscale()





x_loads = range(X_START, X_END + X_STEP, X_STEP)

st_deviation = []
st_load = []

tpl_deviation = []
tpl_load = []

read_to_array("data/tradeoff/tradeoff_deviation_st.csv", st_deviation)
read_to_array("data/tradeoff/tradeoff_load_st.csv", st_load)
read_to_array("data/tradeoff/tradeoff_deviation_tpl.csv", tpl_deviation)
read_to_array("data/tradeoff/tradeoff_load_tpl.csv", tpl_load)

all_arrays = [st_deviation, st_load, tpl_deviation, tpl_load]

for i in all_arrays:
    assert len(i) == 3000
    for row in i:
        assert len(x_loads) == len(row)


# split after load constraints
splitted_st_dev = get_splitted_after_load_constr(st_deviation)


splitted_st_load = get_splitted_after_load_constr(st_load)
splitted_tpl_dev = get_splitted_after_load_constr(tpl_deviation)
splitted_tpl_load = get_splitted_after_load_constr(tpl_load)


print x_loads
print map(lambda x: x/4, x_loads)

#plot_tradeoff(splitted_st_dev, splitted_st_load)
plot_tradeoff(splitted_tpl_dev, splitted_tpl_load)