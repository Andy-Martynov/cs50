from django.shortcuts import render
from django.contrib import messages

import os

import random, math, copy

import numpy as np

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


from mysite import settings

COLORS = 'rgbcmykw'

# 2D
SCALE = 10
SIZE = 100
QSIZE = 25
N = 4
Xmax = 100
Ymax = 100
Zmax = 100

# 3D
CLUSTER_QTY_3D = 500
Xmax3 = 100
Ymax3 = 100
Zmax3 = 100



CENTERS = []
X = None
Y = None
Z = None
Xa = None
Ya = None
Xb = None
Yb = None

def lin(x):
    return x * Ymax / Xmax

def rev(x):
    return (Xmax - x) * Ymax / Xmax

def saw(x):
    if x < Xmax/2:
        return lin(x)
    else:
        return rev(x)

def distance(x1, y1, x2, y2):
    return math.sqrt(math.pow(x1-x2, 2) + math.pow(y1-y2,2))

def rand_uniform_range(n, vmin, vmax):
    """
    Helper function to make an array of random numbers having shape (n, )
    with each number distributed Uniform(vmin, vmax).
    """
    return (vmax - vmin)*np.random.rand(n) + vmin

def rand_normal_range(n, vmin, vmax):
    """
    Helper function to make an array of random numbers having shape (n, )
    with each number distributed Uniform(vmin, vmax).
    """
    return (vmax - vmin)*np.random.normal(loc=0, scale=2, size=(n)) + vmin

#____________________________________________________ INDEX ____________________
def index(request):
    fig = plt.figure(figsize=[19.2, 10.8])

    ax1 = fig.add_subplot(221)
    ax1.plot(range(100))

    x = np.linspace(0, 2, 100)

    ax2 = fig.add_subplot(222)
    ax2.plot(x, x, label='linear')  # Plot some data on the ax2es.
    ax2.plot(x, x**2, label='quadratic')  # Plot more data on the ax2es...
    ax2.plot(x, x**3, label='cubic')  # ... and some more.
    ax2.set_xlabel('x label')  # Add an x-label to the ax2es.
    ax2.set_ylabel('y label')  # Add a y-label to the ax2es.
    ax2.set_title("Simple Plot")  # Add a title to the ax2es.
    ax2.legend()  # Add a legend.

    x0 = np.random.normal(loc=25, scale=SCALE, size=SIZE)
    y0 = np.random.normal(loc=25, scale=SCALE, size=SIZE)
    x1 = np.random.normal(loc=75, scale=SCALE, size=SIZE)
    y1 = np.random.normal(loc=25, scale=SCALE, size=SIZE)
    x2 = np.random.normal(loc=25, scale=SCALE, size=SIZE)
    y2 = np.random.normal(loc=75, scale=SCALE, size=SIZE)
    x3 = np.random.normal(loc=75, scale=SCALE, size=SIZE)
    y3 = np.random.normal(loc=75, scale=SCALE, size=SIZE)

    X = np.concatenate((x0, x1, x2, x3))
    Y = np.concatenate((y0, y1, y2, y3))

    ax3 = fig.add_subplot(223)
    ax3.plot(X, Y, 'ro')

    ax4 = fig.add_subplot(224)

    for i in range(N):
        CENTERS.append(np.random.uniform(0, 100, size=2))
        marker = 'd' + COLORS[i]
        ax3.plot(CENTERS[i][0], CENTERS[i][1], marker, ms=15)


    fn = os.path.join(settings.MEDIA_ROOT, 'learn', 'graph.png')
    fig.savefig(fn)

    graph = os.path.join(settings.MEDIA_URL, 'learn', 'graph.png')

    return render(request, "learn/index.html", {'graph':graph})

# _______________________________________________________ K-MEANS ______________

def k_means_3d(request):
    global X, Y, CENTERS

    fig = plt.figure(figsize=[10.8, 10.8])
    ax = fig.add_subplot(111, projection='3d')

    xs = rand_normal_range(CLUSTER_QTY_3D, -Xmax3, Xmax3)
    ys = rand_normal_range(CLUSTER_QTY_3D, -Ymax3, Ymax3)
    zs = rand_normal_range(CLUSTER_QTY_3D, -Zmax3, Zmax3)
    ax.scatter(xs, ys, zs, marker='o')

    ax.set_xlabel('X Label')
    ax.set_ylabel('Y Label')
    ax.set_zlabel('Z Label')

    fn = os.path.join(settings.MEDIA_ROOT, 'learn', 'graph.png')
    fig.savefig(fn)
    graph = os.path.join(settings.MEDIA_URL, 'learn', 'graph.png')

    return render(request, "learn/k_means.html", {'graph':graph, 'message':'INITIAL', 'mode':'3d'})

def k_means_3d_step(request):
    global X, Y, CENTERS

    fig = plt.figure(figsize=[10.8, 10.8])
    ax = fig.add_subplot(111)

    clusters = dict()
    for i in range(N):
        clusters[i] = [np.array(0), np.array(0)]

    qty = X.shape[0]

    message = ''

    for p in range(qty):
        dist = 1000000
        c = -1
        for i in range(N):
            d = distance(X[p], Y[p], CENTERS[i][0], CENTERS[i][1])
            if d < dist :
                dist = d
                c = i
        clusters[c][0] = np.append(clusters[c][0], X[p])
        clusters[c][1] = np.append(clusters[c][1], Y[p])
        message += f'({X[p]},{Y[p]})->{c} '

    for c in range(N):
        marker = 'o' + COLORS[c]
        ax.plot(clusters[c][0], clusters[c][1], marker)

    for i in range(N):
        marker = 'd' + COLORS[i]
        ax.plot(CENTERS[i][0], CENTERS[i][1], marker, ms=15, mec='k')

    solution = True
    for i in range(N):
        x = np.mean(clusters[i][0])
        y = np.mean(clusters[i][1])
        if x != CENTERS[i][0] or y != CENTERS[i][1]:
            solution = False
        CENTERS[i][0] = x
        CENTERS[i][1] = y
        marker = '*' + COLORS[i]
        ax.plot(CENTERS[i][0], CENTERS[i][1], marker, ms=15, mec='k')


    fn = os.path.join(settings.MEDIA_ROOT, 'learn', 'graph.png')
    fig.savefig(fn)
    graph = os.path.join(settings.MEDIA_URL, 'learn', 'graph.png')
    return render(request, "learn/k_means.html", {'graph':graph, 'clusters':clusters, 'message':'CLUSTERING', 'solution':solution, 'mode':'3d'})



def k_means(request):
    global X, Y, CENTERS

    fig = plt.figure(figsize=[10.8, 10.8])
    ax = fig.add_subplot(111)

    x0 = np.random.normal(loc=25, scale=SCALE, size=SIZE)
    y0 = np.random.normal(loc=25, scale=SCALE, size=SIZE)
    x1 = np.random.normal(loc=75, scale=SCALE, size=SIZE)
    y1 = np.random.normal(loc=25, scale=SCALE, size=SIZE)
    x2 = np.random.normal(loc=25, scale=SCALE, size=SIZE)
    y2 = np.random.normal(loc=75, scale=SCALE, size=SIZE)
    x3 = np.random.normal(loc=75, scale=SCALE, size=SIZE)
    y3 = np.random.normal(loc=75, scale=SCALE, size=SIZE)

    X = np.concatenate((x0, x1, x2, x3))
    Y = np.concatenate((y0, y1, y2, y3))
    ax.plot(X, Y, 'bo')

    CENTERS = []
    for i in range(N):
        CENTERS.append(np.random.uniform(0, 100, size=2))
        # marker = 'd' + COLORS[i]
        # ax.plot(CENTERS[i][0], CENTERS[i][1], marker, ms=15)

    fn = os.path.join(settings.MEDIA_ROOT, 'learn', 'graph.png')
    fig.savefig(fn)
    graph = os.path.join(settings.MEDIA_URL, 'learn', 'graph.png')

    return render(request, "learn/k_means.html", {'graph':graph, 'message':'INITIAL', 'mode':'2d'})

def k_means_step(request):
    global X, Y, CENTERS

    fig = plt.figure(figsize=[10.8, 10.8])
    ax = fig.add_subplot(111)

    clusters = dict()
    for i in range(N):
        clusters[i] = [np.array(0), np.array(0)]

    qty = X.shape[0]

    message = ''

    for p in range(qty):
        dist = 1000000
        c = -1
        for i in range(N):
            d = distance(X[p], Y[p], CENTERS[i][0], CENTERS[i][1])
            if d < dist :
                dist = d
                c = i
        clusters[c][0] = np.append(clusters[c][0], X[p])
        clusters[c][1] = np.append(clusters[c][1], Y[p])
        message += f'({X[p]},{Y[p]})->{c} '

    for c in range(N):
        marker = 'o' + COLORS[c]
        ax.plot(clusters[c][0], clusters[c][1], marker)

    for i in range(N):
        marker = 'd' + COLORS[i]
        ax.plot(CENTERS[i][0], CENTERS[i][1], marker, ms=15, mec='k')

    solution = True
    for i in range(N):
        x = np.mean(clusters[i][0])
        y = np.mean(clusters[i][1])
        if x != CENTERS[i][0] or y != CENTERS[i][1]:
            solution = False
        CENTERS[i][0] = x
        CENTERS[i][1] = y
        marker = '*' + COLORS[i]
        ax.plot(CENTERS[i][0], CENTERS[i][1], marker, ms=15, mec='k')


    fn = os.path.join(settings.MEDIA_ROOT, 'learn', 'graph.png')
    fig.savefig(fn)
    graph = os.path.join(settings.MEDIA_URL, 'learn', 'graph.png')
    return render(request, "learn/k_means.html", {'graph':graph, 'clusters':clusters, 'message':'CLUSTERING', 'solution':solution, 'mode':'2d'})

# ______________________________________________ CLASSIFICATION ______________

def classification(request, delta="0"):
    global X, Y, Xa, Ya, Xb, Yb

    delta = float(delta)

    fig = plt.figure(figsize=[10.8, 10.8])
    ax = fig.add_subplot(111)

    Xa = np.random.uniform(0, Xmax, size=SIZE)
    Xb = np.random.uniform(0, Xmax, size=SIZE)

    X = np.random.uniform(0, Ymax, size=QSIZE)
    Y = np.random.uniform(0, Ymax, size=QSIZE)
    # for i in range(QSIZE):
    #     x = X[i]
    #     Y[i] = x + random.uniform(-0.2*saw(x)*Xmax/Ymax, 0.2*saw(x)*Xmax/Ymax)

    Ya = np.array(0)
    Yb = np.array(0)

    for i in range(SIZE):
        x = Xa[i]
        dx = random.uniform(delta*saw(x)*2/Xmax, saw(x))
        dy = dx * Xmax / Ymax
        Ya = np.append(Ya, x+dy)
        Xa[i] -= dx
    Ya = Ya[1:]
    for i in range(SIZE):
        x = Xb[i]
        dx = random.uniform(delta*saw(x)*2/Xmax, saw(x))
        dy = dx * Xmax / Ymax
        Yb = np.append(Yb, x-dy)
        Xb[i] += dx
    Yb = Yb[1:]

    ax.plot(range(Xmax))
    ax.plot(X, Y, 'go', label='question')
    ax.plot(Xa, Ya, 'bo', label='blue cluster')
    ax.plot(Xb, Yb, 'ro', label='red cluster')
    ax.legend()

    fn = os.path.join(settings.MEDIA_ROOT, 'learn', 'graph.png')
    fig.savefig(fn)
    graph = os.path.join(settings.MEDIA_URL, 'learn', 'graph.png')

    fig = plt.figure(figsize=[10.8, 10.8])
    ax1 = fig.add_subplot(221)
    ax1.hist(Xa, 25)

    fn = os.path.join(settings.MEDIA_ROOT, 'learn', 'graph1.png')
    fig.savefig(fn)
    graph1 = os.path.join(settings.MEDIA_URL, 'learn', 'graph1.png')

    return render(request, "learn/classification.html", {'graph':graph, 'graph1':graph1, 'message':'INITIAL', 'delta':delta,})

def nnc(request, k=1):
    global X, Y, Xa, Ya, Xb, Yb

    fig = plt.figure(figsize=[10.8, 10.8])
    ax = fig.add_subplot(111)

    Xqa = np.array(0)
    Yqa = np.array(0)
    Xqb = np.array(0)
    Yqb = np.array(0)

    for i in range(QSIZE):
        # mina = 1000000
        # minb = 1000000
        Da = []
        Db = []
        for j in range(SIZE):
            # mina = min(mina, distance(X[i], Y[i], Xa[j], Ya[j]))
            Da.append(distance(X[i], Y[i], Xa[j], Ya[j]))
        for j in range(SIZE):
            # minb = min(minb, distance(X[i], Y[i], Xb[j], Yb[j]))
            Db.append(distance(X[i], Y[i], Xb[j], Yb[j]))
        Da.sort()
        Db.sort()
        na = 0
        nb = 0
        for n in range(k):
            if Da[na] < Db[nb]:
                na += 1
            else:
                nb += 1
        # if mina < minb:
        if na > nb:
            Xqa = np.append(Xqa, X[i])
            Yqa = np.append(Yqa, Y[i])
        else:
            Xqb = np.append(Xqb, X[i])
            Yqb = np.append(Yqb, Y[i])
    Xqa = Xqa[1:]
    Yqa = Yqa[1:]
    Xqb = Xqb[1:]
    Yqb = Yqb[1:]

    # ax.plot(range(Xmax))
    ax.plot(Xqa, Yqa, 'b*', label='blue', ms=15, mec='k')
    ax.plot(Xqb, Yqb, 'r*', label='red', ms=15, mec='k')
    ax.plot(Xa, Ya, 'bo', label='blue cluster')
    ax.plot(Xb, Yb, 'ro', label='red cluster')
    ax.legend()

    fn = os.path.join(settings.MEDIA_ROOT, 'learn', 'graph.png')
    fig.savefig(fn)
    graph = os.path.join(settings.MEDIA_URL, 'learn', 'graph.png')

    return render(request, "learn/classification.html", {'graph':graph, 'message':f'{k}-Nearest-Neighbor solution', 'K':k})


def perceptron(request, alpha="0.03", gamma="0.01"):
    global Xa, Ya, Xb, Yb

    alpha = float(alpha)
    gamma = float(gamma)

    W = [0.1, 0.1, 0.1]

    def h(w, x):
        sum = 0
        for i in range(len(w)):
            sum += w[i] * x[i]
        return sum

    def hw(w, x):
        if h(w, x) >= 0:
            return 1
        else:
            return 0

    step=0
    solution = False
    while not solution:
        step += 1
        W_old = copy.deepcopy(W)
        solution = True
        separated = True
        for i in range(SIZE):
            X = [1, Xa[i], Ya[i]]
            y_hw = 0 - hw(W, X)
            if y_hw != 0:
                separated = False
            for j in range(len(W)):
                W[j] += alpha * y_hw * X[j]

            X = [1, Xb[i], Yb[i]]
            y_hw = 1 - hw(W, X)
            if y_hw != 0:
                separated = False
            for j in range(len(W)):
                W[j] += alpha * y_hw * X[j]

        delta = 0
        for j in range(len(W)):
            delta += abs(W[j]-W_old[j])
        if delta > gamma and step < 10000 :
            solution = False
            W_old = copy.deepcopy(W)

    message = f'Peceptron α={alpha} γ={gamma}'

    if not solution:
        messages.info(request, "Solution not found in {step} steps", extra_tags='alert-danger')
    if not separated:
        messages.info(request, "I can not separate the dots by line", extra_tags='alert-danger')

    fig = plt.figure(figsize=[10.8, 10.8])
    ax = fig.add_subplot(111)

    ax.plot(Xa, Ya, 'bo', label='blue cluster')
    ax.plot(Xb, Yb, 'ro', label='red cluster')
    plt.title(f'y={-1*W[0]/W[2]}+{-1*W[1]/W[2]}*x')
    plt.xlabel(f'W={W}')
    plt.ylabel(f'{step} steps, Δ={delta}')


    x = np.linspace(0, SIZE, 100)
    ax.plot(x, -1*(W[0]+x*W[1])/W[2], label='solution')

    ax.legend()

    fn = os.path.join(settings.MEDIA_ROOT, 'learn', 'graph.png')
    fig.savefig(fn)
    graph = os.path.join(settings.MEDIA_URL, 'learn', 'graph.png')

    return render(request, "learn/classification.html", {'graph':graph, 'message': message, 'alpha':alpha, 'gamma':gamma})


# ________________________ MATPLOTLIB __________________________________________

def four_plots(request):
    fig = plt.figure(figsize=[19.2, 10.8])

    ax1 = fig.add_subplot(221)
    ax1.plot(range(100))

    x = np.linspace(0, 2, 100)

    ax2 = fig.add_subplot(222)
    ax2.plot(x, x, label='linear')  # Plot some data on the ax2es.
    ax2.plot(x, x**2, label='quadratic')  # Plot more data on the ax2es...
    ax2.plot(x, x**3, label='cubic')  # ... and some more.
    ax2.set_xlabel('x label')  # Add an x-label to the ax2es.
    ax2.set_ylabel('y label')  # Add a y-label to the ax2es.
    ax2.set_title("Simple Plot")  # Add a title to the ax2es.
    ax2.legend()  # Add a legend.

    x0 = np.random.normal(loc=25, scale=SCALE, size=SIZE)
    y0 = np.random.normal(loc=25, scale=SCALE, size=SIZE)
    x1 = np.random.normal(loc=75, scale=SCALE, size=SIZE)
    y1 = np.random.normal(loc=25, scale=SCALE, size=SIZE)
    x2 = np.random.normal(loc=25, scale=SCALE, size=SIZE)
    y2 = np.random.normal(loc=75, scale=SCALE, size=SIZE)
    x3 = np.random.normal(loc=75, scale=SCALE, size=SIZE)
    y3 = np.random.normal(loc=75, scale=SCALE, size=SIZE)

    X = np.concatenate((x0, x1, x2, x3))
    Y = np.concatenate((y0, y1, y2, y3))

    ax3 = fig.add_subplot(223)
    ax3.plot(X, Y, 'ro')

    ax4 = fig.add_subplot(224)
    mu, sigma = 100, 15
    x = mu + sigma * np.random.randn(10000)

    # the histogram of the data
    n, bins, patches = plt.hist(x, 50, density=1, facecolor='g', alpha=0.75)


    plt.xlabel('Smarts')
    plt.ylabel('Probability')
    plt.title('Histogram of IQ')
    plt.text(60, .025, r'$\mu=100,\ \sigma=15$')
    plt.axis([40, 160, 0, 0.03])
    plt.grid(True)

    for i in range(N):
        CENTERS.append(np.random.uniform(0, 100, size=2))
        marker = 'd' + COLORS[i]
        ax3.plot(CENTERS[i][0], CENTERS[i][1], marker, ms=15)


    fn = os.path.join(settings.MEDIA_ROOT, 'learn', 'graph.png')
    fig.savefig(fn)

    graph = os.path.join(settings.MEDIA_URL, 'learn', 'graph.png')

    return render(request, "learn/index.html", {'graph':graph})
