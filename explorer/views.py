from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.urls import reverse
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.views.decorators.csrf import csrf_exempt

import os
import json
import pickle

import numpy as np
import pandas as pd
import scipy.stats

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
# from mpl_toolkits.mplot3d import Axes3D
# from matplotlib.ticker import (MultipleLocator, AutoMinorLocator)
# from matplotlib import cm

# Set Matplotlib defaults
plt.style.use('seaborn-whitegrid')
# Set Matplotlib defaults
plt.rc('figure', autolayout=True)
plt.rc('axes', labelweight='bold', labelsize='large',
       titleweight='bold', titlesize=18, titlepad=10)

import seaborn as sns
# import plotly.express as px
# import plotly.graph_objs as go
# from plotly.subplots import make_subplots

from sklearn.feature_selection import mutual_info_regression
from sklearn.neighbors import LocalOutlierFactor

from mysite import settings

from common.forms import UploadFileForm

TRAIN = pd.DataFrame()
TEST = pd.DataFrame()
ALL = pd.DataFrame()
PREDICTED = pd.DataFrame()

TARGET = ''
HUE = '---'

PARAMS = {
    'low_score': 0.01,
    'too_many_null_percent': 90,
    'num_values_categorical': 20,
    'n_neighbors_outliers': 2,
    'low_corr': 0.05,
    'high_corr': 0.5,
    }

DROP = set()
TOO_MANY_NULL = set()
LOW_MI_SCORES = set()
LOW_TARGET_CORR = set()
CATEGORICAL = set()
INT_CATEGORICAL = set()
NUMBER = set()

FIGX = 19.2
FIGY = 10.8

DS_LOADED = False

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

# ______________________________________________________________________________

def image_url(name, folder='graphs'):
    return os.path.join(settings.MEDIA_URL, folder, name)

def get_stat_types(df):
    global CATEGORICAL
    global INT_CATEGORICAL
    global NUMBER
    CATEGORICAL = set()
    INT_CATEGORICAL = set()
    NUMBER = set()

    for col in df.columns:
        dtype = str(df[col].dtype)
        if dtype == 'object':
            CATEGORICAL.add(col)
            continue
        v = df[col].astype('str').values
        us = set(v)
        uniques = list(us)
        if dtype != 'float64':
            uniques_count = len(uniques)
            if dtype.startswith('int'):
                if uniques_count < PARAMS['num_values_categorical']:
                    CATEGORICAL.add(col)
                    INT_CATEGORICAL.add(col)
                else:
                    NUMBER.add(col)
        else:
            NUMBER.add(col)


def get_df_info(request, df):
    dtype_colors = {
        'object': 'red',
        'int64': 'blue',
        'int8': 'blue',
        'float64': 'green',
        }

    info = []

    for col in df.columns:
        item  = {}
        item['name'] = col

        dtype = str(df[col].dtype)
        item['dtype'] = dtype
        # messages.info(request, f'dtype: {type(dtype)}', extra_tags='alert-danger')
        if dtype in dtype_colors:
            item['dtype_color'] = dtype_colors[dtype]
        else:
            item['dtype_color'] = 'gray'

        total_count = df.shape[0]
        notnull_count = df[col].count()
        null_count = total_count - notnull_count
        null_percent = 100 * null_count / total_count
        item['total_count'] = total_count
        item['null_count'] = null_count
        item['notnull_count'] = notnull_count
        item['null_percent'] = null_percent
        item['null_percent_color'] = 'black'
        if null_percent == 0 :
            item['null_percent_color'] = 'white'
        if null_percent > 25 :
            item['null_percent_color'] = 'blue'
        if null_percent > 50 :
            item['null_percent_color'] = 'orange'
        if null_percent > 75 :
            item['null_percent_color'] = 'red'

        v = df[col].astype('str').values
        us = set(v)
        u = list(us)
        if 'nan' in u:
            u.remove('nan')
        u.sort()
        uniques = u
        item['values'] = []
        item['uniques'] = ''
        item['uniques_color'] = 'black'

        if dtype != 'float64':
            uniques_count = len(uniques)
            if uniques_count < PARAMS['num_values_categorical']:
                item['uniques'] = uniques_count
                item['values'] = uniques
                if dtype.startswith('int'):
                    item['uniques_color'] = 'red'
        info.append(item)
    return info

def fillnull(request, df):
    X = df.copy()
    for name in X.select_dtypes(["number", 'int64', 'float64']):
        X[name] = X[name].fillna(0)
        X[name] = X[name].astype('float64')
    for name in X.select_dtypes(["category", 'object']):
        X[name] = X[name].fillna('None')
    return X

#____________________________________________________ INDEX ____________________
def index(request):
    global TRAIN
    global TEST
    global ALL
    global PREDICTED

    global DS_LOADED

    global CATEGORICAL
    global INT_CATEGORICAL
    global NUMBER
    global DROP
    global TOO_MANY_NULL

    if not DS_LOADED:
        load_env()
        if os.path.isfile(os.path.join(settings.MEDIA_ROOT, 'tmp', 'explorer', 'train.csv')):
            TRAIN = pd.read_csv(os.path.join(settings.MEDIA_ROOT, 'tmp', 'explorer', 'train.csv'))
        if os.path.isfile(os.path.join(settings.MEDIA_ROOT, 'tmp', 'explorer', 'test.csv')):
            TEST = pd.read_csv(os.path.join(settings.MEDIA_ROOT, 'tmp', 'explorer', 'test.csv'))
        if os.path.isfile(os.path.join(settings.MEDIA_ROOT, 'tmp', 'explorer', 'all.csv')):
            ALL = pd.read_csv(os.path.join(settings.MEDIA_ROOT, 'tmp', 'explorer', 'all.csv'))
        if os.path.isfile(os.path.join(settings.MEDIA_ROOT, 'tmp', 'explorer', 'predicted.csv')):
            PREDICTED = pd.read_csv(os.path.join(settings.MEDIA_ROOT, 'tmp', 'explorer', 'predicted.csv'))
        DS_LOADED = True

    context = {}
    context['target'] = TARGET
    context['columns'] = TRAIN.columns
    context['params'] = PARAMS
    context['hue'] = HUE

    context['train_link'] = os.path.join(settings.MEDIA_URL, 'tmp', 'explorer', 'train.csv')
    context['test_link'] = os.path.join(settings.MEDIA_URL, 'tmp', 'explorer', 'test.csv')
    context['all_link'] = os.path.join(settings.MEDIA_URL, 'tmp', 'explorer', 'all.csv')
    context['predicted_link'] = os.path.join(settings.MEDIA_URL, 'tmp', 'explorer', 'predicted.csv')

    train_shape = TRAIN.shape
    test_shape = TEST.shape
    all_shape = ALL.shape
    predicted_shape = PREDICTED.shape

    context['train_info'] = get_df_info(request, TRAIN)
    context['test_info'] = get_df_info(request, TEST)
    context['all_info'] = get_df_info(request, ALL)
    context['predicted_info'] = get_df_info(request, PREDICTED)

    get_stat_types(TRAIN) # CATEGORICAL, INT_CATEGORICAL, NUMBER
    context['categorical'] = CATEGORICAL
    context['int_categorical'] = INT_CATEGORICAL
    context['number'] = NUMBER
    context['low_target_corr'] = LOW_TARGET_CORR
    context['low_mi_scores'] = LOW_MI_SCORES

    for col in TRAIN.columns:
        total_count = TRAIN.shape[0]
        notnull_count = TRAIN[col].count()
        null_count = total_count - notnull_count
        null_percent = 100 * null_count / total_count
        if null_percent > PARAMS['too_many_null_percent'] :
            TOO_MANY_NULL.add(col)
    context['too_many_null'] = TOO_MANY_NULL


    context['train_shape'] = train_shape
    context['test_shape'] = test_shape
    context['all_shape'] = all_shape
    context['predicted_shape'] = predicted_shape

    df = fillnull(request, TRAIN)

    if TARGET != '' and TARGET in df:
        if train_shape[0] > 0 and predicted_shape[0] > 0:
            fig = plt.figure(figsize=[FIGX, FIGY])
            ax = fig.add_subplot(111)
            sns.kdeplot(data=df[TARGET], color='blue', ax=ax)
            if TARGET in PREDICTED:
                sns.kdeplot(data=PREDICTED[TARGET], color='red', ax=ax)
            name = 'kde2.png'
            fn = os.path.join(settings.MEDIA_ROOT, 'graphs', name)
            fig.savefig(fn, bbox_inches='tight')
            context['kde2'] = image_url(name)

            kdet = scipy.stats.gaussian_kde(df[TARGET])
            if TARGET in PREDICTED:
                kdep = scipy.stats.gaussian_kde(PREDICTED[TARGET])

            grid = np.linspace(df[TARGET].min(), df[TARGET].max(), 500)

            fig = plt.figure(figsize=[FIGX, FIGY])
            ax = fig.add_subplot(111)
            plt.plot(grid, kdet(grid), label="train")
            if TARGET in PREDICTED:
                plt.plot(grid, kdep(grid), label="predicted")
                plt.fill_between(grid, 0, kdet(grid)-kdep(grid), label="difference")
            plt.legend()
            name = 'kde3.png'
            fn = os.path.join(settings.MEDIA_ROOT, 'graphs', name)
            fig.savefig(fn, bbox_inches='tight')
            context['kde3'] = image_url(name)

    return render(request, "explorer/index.html", context)

# __________________________________________________________ MI SCORES _________
def mi_scores(request):
    global LOW_MI_SCORES

    context = {}
    context['target'] = TARGET
    context['columns'] = TRAIN.columns
    context['params'] = PARAMS
    context['hue'] = HUE

    if TARGET in ['', '---']:
        messages.info(request, 'No Target selected', extra_tags='alert-danger')
        return redirect(reverse('explorer:index'))

    X = fillnull(request, TRAIN)
    y = X[TARGET]

    if TARGET in X.columns:
        X.drop([TARGET], axis=1, inplace=True)
    for colname in CATEGORICAL:
        if colname != TARGET:
            X[colname], _ = X[colname].factorize()
    # All discrete features should now have integer dtypes

    discrete_features = [pd.api.types.is_integer_dtype(t) for t in X.dtypes]
    mi_scores = mutual_info_regression(X, y, discrete_features=discrete_features, random_state=0)
    mi_scores = pd.Series(mi_scores, name="MI Scores", index=X.columns)
    mi_scores = mi_scores.sort_values(ascending=False)
    mi_scores = pd.DataFrame(mi_scores)
    mi_scores.columns = ['score']

    LOW_MI_SCORES = list(mi_scores.index[mi_scores['score'] < PARAMS['low_score']])
    context['low_mi_scores'] = LOW_MI_SCORES

    try:
        fig = plt.figure(figsize=[FIGX, FIGY])
        ax = fig.add_subplot(111)
        sns.barplot(y=mi_scores.index, x=mi_scores['score'], ax=ax)
        name = 'mi_scores.png'
        fn = os.path.join(settings.MEDIA_ROOT, 'graphs', name)
        fig.savefig(fn, bbox_inches='tight')
        context['mi_scores'] = image_url(name)
    except:
        messages.info(request, 'index mi_scores fail', extra_tags='alert-danger')

    context['mi_scores_table'] = mi_scores

    return render(request, "explorer/mi_scores.html", context)

# ________________________________________________________ CORRELATION _________
def correlation(request):
    global LOW_TARGET_CORR

    context = {}
    context['target'] = TARGET
    context['columns'] = TRAIN.columns
    context['hue'] = HUE
    context['params'] = PARAMS

    if TARGET in ['', '---']:
        messages.info(request, 'No Target selected', extra_tags='alert-danger')
        return redirect(reverse('explorer:index'))

    corr = TRAIN.corr()
    corr_df = pd.DataFrame(corr)
    target_corr = corr_df[TARGET]
    context['correlations'] = dict(target_corr.sort_values(ascending=False))
    tmp = target_corr.where(target_corr < PARAMS['low_corr']).dropna() #.index.values
    tmp = tmp.where(tmp > -1 * PARAMS['low_corr']).dropna()
    LOW_TARGET_CORR = list(tmp.index)
    context['low_target_corr'] = LOW_TARGET_CORR

    try:
        fig = plt.figure(figsize=[FIGX, FIGY])
        ax = fig.add_subplot(111)
        sns.heatmap(corr, annot=False, ax=ax)
        name = 'corr.png'
        fn = os.path.join(settings.MEDIA_ROOT, 'graphs', name)
        fig.savefig(fn, bbox_inches='tight')
        context['corr'] = image_url(name)
    except:
            messages.info(request, 'corr fail', extra_tags='alert-danger')

    return render(request, "explorer/correlation.html", context)

# ________________________________________________________ OUTLIERS ____________
def get_outliers(request):
    global TRAIN

    context = {}
    context['target'] = TARGET
    context['columns'] = TRAIN.columns
    context['hue'] = HUE

    df = fillnull(request, TRAIN)

    clf = LocalOutlierFactor(n_neighbors=1)
    outliers = clf.fit_predict(df[NUMBER])

    TRAIN['outlier'] = outliers

    return redirect(reverse('explorer:index'))

def get_uniques_count(df, column):
    v = df[column].astype('str').values
    us = set(v)
    u = list(us)
    if 'nan' in u:
        u.remove('nan')
    return len(u)


# ________________________________________________________ COLUMN INFO _________
def column_info(request, dfname, cname):
    global TRAIN
    global TEST
    global ALL

    context = {}
    context['target'] = TARGET
    context['columns'] = TRAIN.columns
    context['params'] = PARAMS
    context['hue'] = HUE

    if TARGET in ['', '---']:
        messages.info(request, 'No Target selected', extra_tags='alert-danger')
        return redirect(reverse('explorer:index'))

    dframes = {'train':TRAIN, 'test':TEST, 'all':ALL, 'predicted':PREDICTED}

    is_categorical = False
    df = dframes[dfname].copy()
    dtype = str(df[cname].dtype)
    v = df[cname].astype('str').values
    us = set(v)
    u = list(us)
    if 'nan' in u:
        u.remove('nan')
    uniques = u
    uniques_count = len(uniques)
    if dtype.startswith('int'):
        if uniques_count < 20:
            is_categorical = True
        else:
            df[cname] = df[cname].astype('float64')

    df = fillnull(request, dframes[dfname])

    target_dtype = df[TARGET].dtype
    target_uniques_counts = get_uniques_count(df, TARGET)

    context['name'] = cname
    dtype = str(df[cname].dtype)
    context['dtype'] = dtype
    context['total'] = df.shape[0]
    context['notnull'] = df[cname].count()
    context['percent'] = 100 * df[cname].count() / df.shape[0]

    if dtype == 'object' :
        context['mode'] = df[cname].mode()[0]
    else:
        context['min'] = df[cname].min()
        context['mean'] = df[cname].mean()
        context['max'] = df[cname].max()
        context['std'] = df[cname].std()

    if dtype == 'object' or is_categorical:
        cname_value_counts = df[cname].value_counts()
        context['value_counts'] = cname_value_counts
        cname_uniques_counts = get_uniques_count(df, cname)

    plots = []

    if cname in NUMBER:
        fig = plt.figure(figsize=[FIGX, FIGY])
        ax = fig.add_subplot(111)
        if HUE != '---':
            sns.histplot(data=df, x=cname, hue=HUE, ax=ax)
        else:
            sns.histplot(data=df[cname], ax=ax)
        name = 'hist.png'
        fn = os.path.join(settings.MEDIA_ROOT, 'graphs', name)
        fig.savefig(fn, bbox_inches='tight')
        plots.append(image_url(name))

        if HUE == '---':
            fig = plt.figure(figsize=[FIGX, FIGY])
            ax = fig.add_subplot(111)
            sns.regplot(x=df[cname], y=df[TARGET], ax=ax)
            name = 'reg.png'
            fn = os.path.join(settings.MEDIA_ROOT, 'graphs', name)
            fig.savefig(fn, bbox_inches='tight')
            plots.append(image_url(name))
        else:
            fig = plt.figure(figsize=[FIGX, FIGY])
            ax = fig.add_subplot(111)
            sns.scatterplot(x=df[cname], y=df[TARGET], hue=df[HUE], palette='Paired_r', ax=ax)
            name = 'reg.png'
            fn = os.path.join(settings.MEDIA_ROOT, 'graphs', name)
            fig.savefig(fn, bbox_inches='tight')
            plots.append(image_url(name))

        fig = plt.figure(figsize=[FIGX, FIGY])
        ax = fig.add_subplot(111)
        sns.scatterplot(data=df, x=cname, y=TARGET, ax=ax)
        name = 'scatter.png'
        fn = os.path.join(settings.MEDIA_ROOT, 'graphs', name)
        fig.savefig(fn, bbox_inches='tight')
        plots.append(image_url(name))

        fig = plt.figure(figsize=[FIGX, FIGY])
        ax = fig.add_subplot(111)
        tmp = pd.DataFrame(df.corr()[cname])
        tmp.sort_values(by=cname, inplace=True)
        tmp = pd.concat([tmp.head(), tmp.tail()])
        sns.heatmap(data=tmp, annot=True)
        name = 'colcorr.png'
        fn = os.path.join(settings.MEDIA_ROOT, 'graphs', name)
        fig.savefig(fn, bbox_inches='tight')
        plots.append(image_url(name))

    if cname in CATEGORICAL:
        if target_uniques_counts > 4:
            fig = plt.figure(figsize=[FIGX, FIGY])
            ax = fig.add_subplot(111)
            if HUE != '---':
                sns.boxplot(data=df, x=cname, y=TARGET, hue=HUE, ax=ax)
            else:
                sns.boxplot(data=df, x=cname, y=TARGET, ax=ax)
            name = 'box.png'
            fn = os.path.join(settings.MEDIA_ROOT, 'graphs', name)
            fig.savefig(fn, bbox_inches='tight')
            plots.append(image_url(name))

        if cname_uniques_counts < 15 and  target_uniques_counts < 5:
            fig = plt.figure(figsize=[FIGX, FIGY])
            ax = fig.add_subplot(111)
            sns.countplot(data=df, x=cname, hue=TARGET, ax=ax)
            name = 'count.png'
            fn = os.path.join(settings.MEDIA_ROOT, 'graphs', name)
            fig.savefig(fn, bbox_inches='tight')
            plots.append(image_url(name))

        if cname_uniques_counts < 15 and target_uniques_counts > 2:
            fig = plt.figure(figsize=[FIGX, FIGY])
            ax = fig.add_subplot(111)
            sns.swarmplot(data=df, x=cname, y=TARGET, ax=ax)
            name = 'swarm.png'
            fn = os.path.join(settings.MEDIA_ROOT, 'graphs', name)
            fig.savefig(fn, bbox_inches='tight')
            plots.append(image_url(name))

    context['plots'] = plots

    return render(request, "explorer/column_info.html", context)

# ___________________________________________________ SET TARGET, HUE __________
def save_env():
    env = {}
    env['target'] = TARGET
    env['hue'] = HUE
    env['params'] = PARAMS
    pickle.dumps(env, os.path.join(settings.MEDIA_ROOT, 'tmp', 'explorer', 'env.pickle'))

def load_env():
    global PARAMS
    global TARGET
    global HUE
    if os.path.isfile(os.path.join(settings.MEDIA_ROOT, 'tmp', 'explorer', 'env.pickle')):
        env = pickle.load(os.path.join(settings.MEDIA_ROOT, 'tmp', 'explorer', 'env.pickle'))
        TARGET = env['target']
        HUE = env['hue']
        PARAMS = env['params']

@csrf_exempt
def set_param(request):
    global PARAMS
    global TARGET
    global HUE
    if request.method == 'POST' :
        data = json.loads(request.body)
        if data.get("param") is not None:
            param = data["param"]
            if data.get("value") is not None:
                value = data["value"]
                if param == 'target':
                    TARGET = value
                    save_env()
                    return HttpResponse(status=200)
                if param == 'hue':
                    HUE = value
                    save_env()
                    return HttpResponse(status=200)
                PARAMS[param] = float(value)
                save_env()
                return HttpResponse(status=200)
            return HttpResponse(status=401)
        return HttpResponse(status=402)
    else:
        return HttpResponse(status=400)

# _______________________________________________________ LOAD _________________
def load_dataset(request, mode='train'):
    global TRAIN
    global TEST
    global ALL
    global PREDICTED

    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        file = request.FILES['file']
        if form.is_valid():
            fs = FileSystemStorage()
            fn = os.path.join('tmp', 'explorer', file.name)
            if fs.exists(fn) :
                fs.delete(fn)
            filename = fs.save(fn, file)

            try:
                if mode == 'train':
                    TRAIN = pd.read_csv(os.path.join(settings.MEDIA_ROOT, filename))
                    TRAIN.to_csv(os.path.join(settings.MEDIA_ROOT, 'tmp', 'explorer', 'train.csv'), index=False)
                    TEST = pd.DataFrame()
                    ALL = pd.DataFrame()
                    PREDICTED = pd.DataFrame()
                elif mode == 'test':
                    TEST = pd.read_csv(os.path.join(settings.MEDIA_ROOT, filename))
                    TEST.to_csv(os.path.join(settings.MEDIA_ROOT, 'tmp', 'explorer', 'test.csv'), index=False)
                else:
                    PREDICTED = pd.read_csv(os.path.join(settings.MEDIA_ROOT, filename))
                    PREDICTED.to_csv(os.path.join(settings.MEDIA_ROOT, 'tmp', 'explorer', 'predicted.csv'), index=False)
                ALL = pd.concat([TRAIN, TEST])
                ALL.to_csv(os.path.join(settings.MEDIA_ROOT, 'tmp', 'explorer', 'all.csv'), index=False)
                return redirect(reverse('explorer:index'))
            except:
                messages.info(request, 'Error loading dataset', extra_tags='alert-danger')
                form = UploadFileForm()
                return render(request, 'common/upload.html', {'form': form, 'title':'Upload dataset'})

        else:
            messages.info(request, 'form is NOT valid', extra_tags='alert-danger')
            form = UploadFileForm()
            return render(request, 'common/upload.html', {'form': form, 'title':'Upload dataset'})
    else:
        form = UploadFileForm()
        return render(request, 'common/upload.html', {'form': form, 'title':'Upload dataset'})
