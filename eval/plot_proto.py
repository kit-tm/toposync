import matplotlib.pyplot as plt
import numpy as np

def to_array(file_name):
    values = []
    with open(file_name) as file:
        for line in file.readlines():
            values.append(int(line))
    return values

tpl_tbs4 = to_array('data/logs_proto/tpl/clear/tbs4.log')
tpl_tbs10 = to_array('data/logs_proto/tpl/clear/tbs10.log')
tpl_tbs11 = to_array('data/logs_proto/tpl/clear/tbs11.log')
tpl_tbs21 = to_array('data/logs_proto/tpl/clear/tbs21.log')

tpl = [tpl_tbs4, tpl_tbs10, tpl_tbs11, tpl_tbs21]

ref_tbs4 = to_array('data/logs_proto/ref/clear/tbs4.log')
ref_tbs10 = to_array('data/logs_proto/ref/clear/tbs10.log')
ref_tbs11 = to_array('data/logs_proto/ref/clear/tbs11.log')
ref_tbs21 = to_array('data/logs_proto/ref/clear/tbs21.log')

ref = [ref_tbs4, ref_tbs10, ref_tbs11, ref_tbs21]


dsts = ['destination1', 'destination3', 'destination4', 'destination2']
idxs = [0,3,1,2]
x = range(33)

for i in idxs:
    print(ref[i])
    plt.plot(x, ref[i], label=dsts[i], marker='x')

plt.xlabel('packet index')
plt.ylabel('delay [in ms]')
plt.legend(bbox_to_anchor=(1,0.5))

plt.show()

for i in idxs:
    print(tpl[i])
    plt.plot(x, tpl[i], label=dsts[i], marker='x')

plt.xlabel('packet index')
plt.ylabel('delay [in ms]')
plt.ylim(750, 900)
plt.yticks(range(750, 900, 25))
plt.legend()

plt.show()