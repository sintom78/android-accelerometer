import matplotlib.pyplot as pyplot
import matplotlib.figure as figure
import matplotlib.cm as cm
from mpl_toolkits.mplot3d import Axes3D

def plot2D(data,figure=1,title="",show=True):
    pyplot.figure(figure)
    n = 0
    if (len(data) == 2):
        sb = 211
    elif (len(data)>2 and len(data)<4):
        sb = 221
    else:
        sb = 111
    for d in data:
        pyplot.subplot(sb)
        for dd in d['data']:
#            print dd
            pyplot.plot(dd)

        pyplot.grid()
        pyplot.legend(d['legend'])
        n=n+1
        sb=sb+1

    pyplot.title(title)
    if (show == True):
        pyplot.show()


def plot3D(x,fx,y,fy,z,fz,mod,fmod):
    fig = pyplot.figure()
    ax = Axes3D(fig)
    ax.plot(xs=fx,ys=fy,zs=fz) #,rstride=1,cstride=1,cmap=cm.jet)
    pyplot.show()


