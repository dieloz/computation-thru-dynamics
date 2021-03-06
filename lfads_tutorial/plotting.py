# Copyright 2019 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


"""Plotting functions for LFADS and the data RNN example."""


from __future__ import print_function, division, absolute_import

import matplotlib.pyplot as plt
import numpy as onp

from sklearn.decomposition import PCA


def plot_data_pca(data_dict):
  """Plot the PCA skree plot of the hidden units in the integrator RNN."""
  f = plt.figure()
  ndata = data_dict['hiddens'].shape[0]
  print(data_dict.keys())
  print(data_dict['hiddens'].shape)
  pca = PCA(n_components=100)
  pca.fit(onp.reshape(data_dict['hiddens'], [10240 * 25, 100]))

  plt.plot(onp.arange(1, 16), onp.cumsum(pca.explained_variance_ratio_)[0:15],
           '-o');
  plt.plot([1, 15], [0.95, 0.95])
  plt.xlabel('PC #')
  plt.ylabel('Cumulative Variance')
  plt.xlim([1, 15])
  plt.ylim([0.3, 1]);
  return f


def plot_data_example(input_bxtxu, hidden_bxtxn=None,
                      output_bxtxo=None, target_bxtxo=None, bidx=None):
  """Plot a single example of the data from the data integrator RNN."""
  if bidx is None:
    bidx = onp.random.randint(0, input_bxtxu.shape[0])
  ntoplot = 10
  ntimesteps = input_bxtxu.shape[1]
  f = plt.figure(figsize=(10,5))
  plt.subplot(311)
  plt.plot(input_bxtxu[bidx,:,0])
  plt.xlim([0, ntimesteps-1])
  plt.ylabel('Input')
  plt.title('Example %d'%bidx)
  if hidden_bxtxn is not None:
    plt.subplot(312)
    plt.plot(hidden_bxtxn[bidx, :, 0:ntoplot])
    plt.ylabel('Hiddens')
    plt.xlim([0, ntimesteps-1]);
  plt.subplot(414)
  if output_bxtxo is not None:
    plt.plot(output_bxtxo[bidx,:,0].T, 'r');
    plt.xlim([0, ntimesteps-1]);
    plt.ylabel('Output / Targets')
  if target_bxtxo is not None:
    plt.plot(target_bxtxo[bidx,:,0], 'k');
    plt.xlim([0, ntimesteps-1]);
  return f


def plot_data_stats(data_dict, data_bxtxn, data_dt):
  """Plot the statistics of the data integrator RNN data after spikifying."""
  print(onp.mean(onp.sum(data_bxtxn, axis=1)), "spikes/second")
  f = plt.figure(figsize=(12,4))
  plt.subplot(141)
  plt.hist(onp.mean(data_bxtxn, axis=1).ravel()/data_dt);
  plt.xlabel('spikes / sec')
  plt.subplot(142)
  plt.imshow(data_dict['hiddens'][0,:,:].T)
  plt.xlabel('time')
  plt.ylabel('neuron #')
  plt.title('Sample trial rates')
  plt.subplot(143);
  plt.imshow(data_bxtxn[0,:,:].T)
  plt.xlabel('time')
  plt.ylabel('neuron #')
  plt.title('spikes')
  plt.subplot(144)
  plt.stem(onp.mean(onp.sum(data_bxtxn, axis=1), axis=0));
  plt.xlabel('neuron #')
  plt.ylabel('spikes / sec');
  return f


def plot_losses(tlosses, elosses, sampled_every=1, start_idx=0, stop_idx=None):
  """Plot the losses associated with training LFADS."""
  lidx = 1
  nlosses = len(tlosses.keys())
  f = plt.figure(figsize=(15, 8))
  for k in tlosses:
    plt.subplot(2, 3, lidx)
    tl = tlosses[k].shape[0]
    x = onp.arange(start_idx, stop_idx, sampled_every)
    lidx_start = int(start_idx/sampled_every)
    lidx_stop = int(stop_idx/sampled_every)
    y = tlosses[k][lidx_start:lidx_stop]
    plt.plot(x, y, 'k')
    y = elosses[k][lidx_start:lidx_stop]
    plt.plot(x, y, 'r')
    plt.axis('tight')
    plt.title(k)
    lidx += 1
  return f


def plot_priors(params):
  """Plot the parameters of the LFADS priors."""
  prior_dicts = {'ic' : params['ic_prior'], 'ii' : params['ii_prior']}
  pidxs = (pidx for pidx in onp.arange(1,12))
  f = plt.figure(figsize=(12,6))
  for k in prior_dicts:
    for j in prior_dicts[k]:
      plt.subplot(2,3,next(pidxs));
      data = prior_dicts[k][j]
      if "log" in j:
        data = onp.exp(data)
        j_title = j.strip('log')
      else:
        j_title = j
      plt.stem(data)
      plt.title(k + ' ' + j_title)
  return f


def plot_lfads(x_txd, avg_lfads_dict, data_dict=None, dd_bidx=None,
               ii_scale=1.0):
  """Plot the full state ofLFADS operating on a single example."""
  print("bidx: ", dd_bidx)
  ld = avg_lfads_dict

  f = plt.figure(figsize=(12,6))
  plt.subplot(161)
  plt.imshow(x_txd.T)
  plt.title('x')

  plt.subplot(162)
  plt.imshow(ld['xenc_t'].T)
  plt.title('x enc')

  plt.subplot(163)
  plt.imshow(ld['gen_t'].T)
  plt.title('generator')

  plt.subplot(164)
  factors = ld['factor_t']
  plt.imshow(factors.T)
  plt.title('factors')

  d_max = None
  d_min = None
  if data_dict is not None:
    d_max = onp.max(data_dict['hiddens'][dd_bidx])
    d_min = onp.min(data_dict['hiddens'][dd_bidx])
    plt.subplot(166)
    plt.imshow(data_dict['hiddens'][dd_bidx].T)
    plt.title('True rates')

  plt.subplot(165)
  if d_max is not None: # Handle color saturation for viewing.
    rates = onp.exp(ld['lograte_t'])
    rates = onp.where(rates > 2*d_max, 2*d_max, rates)
    rates = onp.where(rates < 2*d_min, 2*d_min, rates)
  plt.imshow(rates.T)
  plt.title('rates')

  plt.figure(figsize=(12,6))
  plt.subplot(131)
  ic_mean = ld['ic_mean']
  ic_std = onp.exp(0.5*ld['ic_logvar'])
  plt.stem(ic_mean)
  plt.plot(ic_mean + ic_std, 'r')
  plt.plot(ic_mean - ic_std, 'r')
  plt.title('g0')

  plt.subplot(132)
  plt.imshow(ld['c_t'].T)
  plt.title('controller')

  plt.subplot(133)
  ii_mean = ld['ii_mean_t']
  plt.plot(ii_mean, 'b')
  if data_dict is not None:
    plt.plot(ii_scale*data_dict['inputs'][dd_bidx], 'm', lw=3)
  plt.plot(ld['ii_t'], 'k')
  plt.title('inferred input')

  return f
