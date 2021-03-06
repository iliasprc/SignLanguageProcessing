import h5py
import re
import random
import math

import numpy

import tensorflow as tf
import keras
from keras.models import Sequential, Model
from keras.layers import Dense, Add, Dropout
from keras import backend as K
from keras.layers import Layer, Input, Bidirectional, LSTM, GRU, Embedding, Multiply, BatchNormalization, Concatenate, Add, Lambda, Subtract
from keras.utils import to_categorical

from modeling import *
from data import *
from training import *
import accumulators
from dtw import dtw, fakedtw
from utils import *

from model_FF_20200604 import *


# file with the best (on stop set) results
fname_model_weights = "models/%s-clear.h5" % model_ID

# file with an example of the chosen output
fname_example = "temp/%s-clear-example.txt" % model_ID

list_training = loadList("data/training.list")
list_stop = loadList("data/stop.list")

# cleaning sets
list_clear = loadList("data/clear.list")
list_training = [key for key in list_training if key in list_clear]
list_stop = [key for key in list_stop if key in list_clear]

random.shuffle(list_training)
random.shuffle(list_stop)

# for debuging
list_stop = list_stop[0:256]
#list_stop = list_stop[0:1]

n_files_in_batch = 256
if n_files_in_batch > len(list_training):
  n_files_in_batch = len(list_training) # carefull

# how often is model evaluated using the stop set.
# 1 means after every reestimation 
n_batches = 1

# when stop training
max_steps = 10 * len(list_training)

optimizer = accumulators.AdamAccumulate(lr=0.001, decay=0.0, accum_iters=n_files_in_batch)

wMSE = 0.2 # weight for MSE loss
wATT = 2.0 / 98.0 # weight for our attention based loss loss

training(
  model4training=model4training,
  model4output=model4output,
  model4example=model4example,
  datamod4training=synch, 
  loss=len(ys)*[MSE]+len(ys_att)*[lambda y_true, y_pred: lossAttMSE(y_true, y_pred, thr=0.2)],
  wloss=len(ys)*[wMSE]+len(ys_att)*[wATT],
  loader=loader,
  list_training=list_training,
  list_stop=list_stop,
  mask4print="%.4f",
  optimizer=optimizer,
  testing_interval=n_batches*n_files_in_batch,
  fname_example=fname_example,
  fname_model_weights=fname_model_weights,
  funs_eval=len(ys)*[compute_errorMSEDTW],
  max_steps=max_steps,
)
  
hfTar.close()
