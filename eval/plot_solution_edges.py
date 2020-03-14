import matplotlib.pyplot as plt
import csv
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('path', help="path of csv file", type=str)
args = parser.parse_args()

x = [0,2,0,1,2,0,1,2,1,2]
y = [0,0,1,1,1,2,2,2,3,3]
nodes = {"s1":(1,3), "s2":(2,3), "s3":(1,2), "s4":(2,2), "s5":(1,1), "s6":(2,1), "s7":(0,2), "s8":(0,1), "s9":(2,0),"s10":(0,0)}


def drawArrow(A, B):
    plt.arrow(A[0], A[1], B[0] - A[0], B[1] - A[1], 
               head_width=0.08,head_length=0.175,length_includes_head=True, color='r')
    plt.scatter([A[0],B[0]],[A[1],B[1]],s=500, color='#1f77b4')

def plotEdge(t1, t2, arrow=False):
    if arrow:
        print("drawing arrow from %s to %s" % (t1,t2))
        drawArrow(t1,t2)
    else:
        plt.plot([t1[0],t2[0]],[t1[1],t2[1]], 'k')

def plotTopology(node_alpha, topo_title=True):
    if topo_title:
        plt.title("Topology (capacity of each link=10)")
    turnOffTicks()
    plotNodes(node_alpha)
    plotEdge(nodes["s1"], nodes["s2"])
    plotEdge(nodes["s1"], nodes["s3"])
    plotEdge(nodes["s4"], nodes["s2"])
    plotEdge(nodes["s3"], nodes["s4"])
    plotEdge(nodes["s3"], nodes["s7"])
    plotEdge(nodes["s3"], nodes["s5"])
    plotEdge(nodes["s4"], nodes["s6"])
    plotEdge(nodes["s4"], nodes["s5"])
    plotEdge(nodes["s7"], nodes["s5"])
    plotEdge(nodes["s7"], nodes["s8"])
    plotEdge(nodes["s6"], nodes["s5"])
    plotEdge(nodes["s8"], nodes["s5"])
    plotEdge(nodes["s8"], nodes["s10"])
    plotEdge(nodes["s9"], nodes["s6"])

def turnOffTicks():
                plt.tick_params(
                    axis='both',     
                    which='both',      # both major and minor ticks are affected
                    bottom=False,     
                    top=False,     
                    labelbottom=False,
                    labelleft=False,
                    labelright=False,
                    labeltop=False,
                    left=False,
                    right=False) 

def plotNodes(alpha):
    plt.scatter(x,y, marker='o', s=500, alpha=alpha, label='topology nodes')

def plotSource(name):
    coords = nodes[name]
    plt.scatter(coords[0], coords[1], marker='o', s=500, alpha=1.0, color='g', label='source')

def plotDestinations(names):
    x_coords = []
    y_coords = []
    for name in names:
        coords = nodes[name]
        x_coords.append(coords[0])
        y_coords.append(coords[1])
        print("plotting dst " + name + ": (%s,%s)" % coords)
    plt.scatter(x_coords, y_coords, marker='o', s=500, alpha=1.0, color='k', label='destination')

def plotPlacement(placements):
    x_coords = []
    y_coords = []
    name_to_type = {}

    if placements[0] == "NO":
        return

    for placement in placements:
        vnf_type, name = placement.split('@')
        if name_to_type.get(name) is None:
            name_to_type[name] = []
        name_to_type[name].append(vnf_type)

    print(name_to_type)

    for name, vnf_types in name_to_type.iteritems():
        x_annotation_offset = 13
        y_annotation_offset = 10
        coords = nodes[name]
        x_coords.append(coords[0])
        y_coords.append(coords[1])
        for vnf_type in vnf_types:
            ax.annotate(vnf_type, (coords[0],coords[1]), xytext=(x_annotation_offset,y_annotation_offset),textcoords='offset points')
            y_annotation_offset -= 10

        
        
    
    #plt.scatter(x_coords, y_coords, s=500, alpha=0.5,marker='o', color='g', label='placement')



plot_cnt = 0
plot_idx = 1
rows = []
with open(args.path) as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        rows.append(row)
        if len(row) == 0:
            plot_cnt += 1
    print(plot_cnt)
    row_cnt = (plot_cnt + 1) / 3 # +1 because topo is also one plot
    if (plot_cnt + 1) % 3 >= 1:
        row_cnt += 1
    print(row_cnt)

    fig, axes = plt.subplots(row_cnt, 3)
    fig.suptitle("%s, value: %s" %(rows[0][0], rows[0][1]), fontsize=16)


    plt.subplot(row_cnt, 3, plot_idx)
    plot_idx += 1
    plotTopology(1.0)


    start_subplot = True
    start_placement = False
    source = None
    destinations = []
    placements = []
    edges = []
    for row in rows[1:]:
        print(row)
        if len(row) == 0:
            start_subplot = True

            plotNodes(0.0)

            for edge in edges:
                plotEdge(nodes[edge[0]], nodes[edge[1]], arrow=True)

            plotSource(source)
            
            plotDestinations(destinations)

            plotPlacement(placements)
            handles, labels = ax.get_legend_handles_labels()
            fig.legend(handles, labels)


            source = None
            destinations = []
            placements = []
            edges = []
        else:
            if start_subplot:
                ax = plt.subplot(row_cnt, 3, plot_idx)
                turnOffTicks()
                plt.title("tree for flow %s, demand: %s" % ((plot_idx - 1), row[0]))
                source = row[1]
                destinations = row[2:]

                plot_idx += 1
                start_subplot = False
                start_placement = True
            elif start_placement:
                placements = row
                start_placement = False
            else:
                edges.append((row[0], row[1]))


# turn off ticks for remaining empty subplots
if plot_idx <= (row_cnt * 3):
    for i in range(plot_idx, (row_cnt * 3) + 1):
        plt.subplot(row_cnt, 3, i)
        turnOffTicks()
            
        
plt.subplots_adjust(left=0.01, bottom=0.01, right=0.99, top=0.92, wspace=0.05, hspace=0.075)
plt.show()