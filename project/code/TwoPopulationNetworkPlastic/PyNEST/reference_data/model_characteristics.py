'''

Performs some basic data analyses on the recorded reference data and 
stores resulting statistics in a json file */model_characteristics.json.

'''

import sys
sys.path.append(r'../')
import model

import matplotlib.pyplot as plt
from matplotlib import gridspec
import nest
import numpy as np
import os
    
##########################################################
def data_statistics(data):
    '''
    Calculates and collects simple statistics for a list of data samples.

    Arguments
    ---------
    data:  list, numpy.ndarray
           Ensemble of (scalar) data samples.

    Returns
    -------
    stats: dict
           Dictionary containing
           - mean               (stats['mean'])
           - median             (stats['median'])
           - standard deviation (stats['sd'])
           - minimum            (stats['min'])
           - maximum            (stats['max'])
           across the emsemble of data samples.

    '''
    stats = {}
    stats['mean'] = np.nanmean(data)
    stats['sd'] = np.nanstd(data)
    stats['min'] = np.nanmin(data)
    stats['max'] = np.nanmax(data)
    stats['median'] = np.nanmedian(data)
    
    return stats
##########################################################
def input_spike_count_statistics(pop_pre,pop_post, binsize, time_interval, model_instance, spike_file_label):
    '''
    Calculates statistics of input spikes across ensemble of time steps and across neuron population.

    Arguments
    ---------
    pop_pre:        nest.NodeCollection
                    Ensemble of source neurons accounted for when calculating total number of input spikes.

    pop_post:       nest.NodeCollection
                    Ensemble of target neurons.

    binsize:        float
                    Binsize for analysis of input spikes (ms)

    time_interval:  tuple
                    Start and stop time for evaluation of input spike statistics (ms).

    model_instance: model.Model
                    Instance of the network model.

    spike_file_label: str
                      Root of name of file containing spike data.

    Returns
    -------
    in_spike_count_stats: dict
                     Dictionary containing
                     - population averaged mean number of input spikes      (in_spike_count_stats['mean_popav'])
                     - population averaged maximum number of input spikes   (in_spike_count_stats['max_popav'])
                     - population minimum of maximum number of input spikes (in_spike_count_stats['max_popmin'])
                     - population maximum of maximum number of input spikes (in_spike_count_stats['max_popmax'])
                     - metadata for data analysis (in_spike_count_stats['metadata']) with 
                       + size of source populations (metadata['pop_pre_size'])
                       + size of target populations (metadata['pop_post_size'])
                       + time interval (metadata['time_interval'])
                       + binsize (metadata['binsize'])    
    '''

    print()
    print('Statistics of input spike counts across time and population (binsize =%.3f ms)' % binsize)
    print('-------------------------------------------------------------------------------')

    
    ## load spikes from reference data
    spikes = model.load_spike_data(model_instance.pars['data_path'], spike_file_label, time_interval, pop_pre)
    
    ## load connectivity
    C = model_instance.get_connectivity(pop_pre, pop_post)
    sources = C[:,0]
    targets = C[:,1]
   
    times = np.arange(time_interval[0],time_interval[1]+binsize,binsize)    
    stats = []

    in_spike_count_mean = []
    in_spike_count_max = []

    for cn,nid in enumerate(pop_post):  ## loop over all (postsynaptic) neurons
        print("%d/%d neurons (%d%%) completed" % (cn+1, len(pop_post), 1.*(cn+1)/len(pop_post)*100), end = '\r')
        ind = np.where(targets==nid)[0]
        pre_pop = sources[ind] ## pool of neurons presynaptic to nid
        in_spikes = []  ## lopp over all neurons presynaptic to nid
        for pre in pre_pop:    
            ind = np.where(spikes[:,0]==pre)[0]
            in_spikes += list(spikes[ind,1])  ## add spikes of presynaptic neuron pre
            
        in_spikes = np.sort(in_spikes)
        in_spike_count_hist = np.histogram(in_spikes,times)[0]
        stats = data_statistics(in_spike_count_hist)
        in_spike_count_mean += [stats['mean']]  ## time averaged number of input spikes
        in_spike_count_max += [stats['max']]    ## maximum number of input spikes

    in_spike_count_stats = {}
    in_spike_count_stats['mean_popav'] = np.mean(in_spike_count_mean)  ## population averaged mean number of input spikes
    in_spike_count_stats['max_popav'] = np.mean(in_spike_count_max)    ## population averaged maximum number of input spikes
    in_spike_count_stats['max_popmin'] = int(np.min(in_spike_count_max))    ## population minimum of maximum number of input spikes
    in_spike_count_stats['max_popmax'] = int(np.max(in_spike_count_max))    ## population maximum of maximum number of input spikes

    print()
    print()
    print("\t- mean, population average: %.2f" % in_spike_count_stats['mean_popav'])
    print("\t- maximum, population average: %.3f " % in_spike_count_stats['max_popav'])
    print("\t- maximum, population minimum: %d " % in_spike_count_stats['max_popmin'])
    print("\t- maximum, population maximum: %d " % in_spike_count_stats['max_popmax'])
    print()

    ## store metadata
    metadata = {}
    metadata['pop_pre_size'] = len(pop_pre)
    metadata['pop_post_size'] = len(pop_post)
    metadata['time_interval'] = time_interval
    metadata['binsize'] = binsize
    metadata['function'] = sys._getframe(  ).f_code.co_name
    metadata['file'] = sys._getframe(  ).f_code.co_filename
    in_spike_count_stats['metadata'] = metadata
    
    return in_spike_count_stats

##########################################################
def time_averaged_firing_rate_statistics(pop, time_interval, model_instance, spike_file_label):
    '''
    Calculates statistics of time averaged firing rates across across neuron population.

    Arguments
    ---------
    pop:            nest.NodeCollection
                    Ensemble of neurons accounted for when calculating statistics of time averaged firing rates.

    time_interval:  tuple
                    Start and stop time (in ms) for evaluation of time averaged rates.

    model_instance: model.Model
                    Instance of the network model.

    spike_file_label: str
                      Root of name of file containing spike data.

    Returns
    -------
    rate_stats:     dict
                    Dictionary containing
                    - mean               (rate_stats['mean'])
                    - median             (rate_stats['median'])
                    - standard deviation (rate_stats['sd'])
                    - minimum            (rate_stats['min'])
                    - maximum            (rate_stats['max'])
                    of time averaged firing rates across the emsemble of neurons, and
                    - metadata for data analysis (rate_stats['metadata']) with 
                       + size of neuron population (metadata['pop_size'])
                       + time interval (metadata['time_interval'])
    '''

    print()
    print('Statistics of time averaged firing across population')
    print('----------------------------------------------------')
    
    D = time_interval[1]-time_interval[0]

    ## load spikes from reference data
    spikes = model.load_spike_data(model_instance.pars['data_path'], spike_file_label, time_interval, pop)
    
    rates = []
    for cn,nid in enumerate(pop):  ## loop over all neurons
        print("%d/%d neurons (%d%%) completed" % (cn+1, len(pop), 1.*(cn+1)/len(pop)*100), end = '\r')        
        ind = np.where(spikes[:,0]==nid)[0]
        n_events = len(ind)        
        rates += [n_events/ D * 1000.0]
    rate_stats = data_statistics(rates)

    print()
    print()
    print("\t- mean: %.2f/s" % rate_stats['mean'])
    print("\t- median: %.2f/s" % rate_stats['median'])
    print("\t- standard deviation: %.2f/s" % rate_stats['sd'])
    print("\t- minimum: %.2f/s" % rate_stats['min'])
    print("\t- maximum: %.2f/s" % rate_stats['max'])    
    print()

    ## store metadata
    metadata = {}
    metadata['pop_size'] = len(pop)
    metadata['time_interval'] = time_interval
    metadata['function'] = sys._getframe(  ).f_code.co_name
    metadata['file'] = sys._getframe(  ).f_code.co_filename
    rate_stats['metadata'] = metadata

    #rs = np.arange(0.,10.,1.0); rates_hist = np.histogram(rates,rs)[0]; figure(1);clf();plot(rs[:-1],rates_hist)
    return rate_stats

##########################################################
def population_spike_count_statistics(pop, binsize, time_interval, model_instance, spike_file_label):
    '''
    Calculates statistics of population spike count (total number of spikes in each time bin) across time.

    Note that the population spike count is NEITHER normalized by the population size nor the binsize.

    Arguments
    ---------
    pop:            nest.NodeCollection
                    Ensemble of neurons accounted for when calculating population spike count.

    binsize:        float
                    Binsize for evaluation of population spike count signal (ms).

    time_interval:  tuple
                    Start and stop time (in ms) for evaluation of population spike count signal.

    model_instance: model.Model
                    Instance of the network model.

    spike_file_label: str
                      Root of name of file containing spike data.

    Returns
    -------
    pop_spike_count_stats: dict
                    Dictionary containing
                    - mean               (pop_spike_count_stats['mean'])
                    - median             (pop_spike_count_stats['median'])
                    - standard deviation (pop_spike_count_stats['sd'])
                    - minimum            (pop_spike_count_stats['min'])
                    - maximum            (pop_spike_count_stats['max'])
                    of population spike counts, and
                    - metadata for data analysis (pop_spike_count_stats['metadata']) with 
                       + size of neuron population (metadata['pop_size'])
                       + time interval (metadata['time_interval'])
                       + binsize (metadata['binsize'])    

    pop_spike_count:  numpy.ndarray
                      Array containing population spike count for each time bin (number of spikes per time bin).
   
    times:          numpy.ndarray
                    Array containing time points at which population spike count is calculated (ms).

    '''

    print()
    print('Statistics of population spike counts across time (binsize = %.3f ms)' % binsize)
    print('----------------------------------------------------------------------')
    
    D = time_interval[1]-time_interval[0]

    ## load spikes from reference data
    spikes = model.load_spike_data(model_instance.pars['data_path'], spike_file_label, time_interval, pop)    
        
    times = np.arange(time_interval[0],time_interval[1]+binsize,binsize)    
    pop_spike_count = np.histogram(spikes[:,1],times)[0]
    # figure(1);clf();plot(times[:-1],pop_spike_count)

    pop_spike_count_stats = data_statistics(pop_spike_count)
    pop_spike_count_stats['min'] = int(pop_spike_count_stats['min'])
    pop_spike_count_stats['max'] = int(pop_spike_count_stats['max'])    

    print()
    print("\t- mean: %.2f" % pop_spike_count_stats['mean'])
    print("\t- median: %.2f" % pop_spike_count_stats['median'])
    print("\t- standard deviation: %.2f" % pop_spike_count_stats['sd'])
    print("\t- minimum: %d" % pop_spike_count_stats['min'])
    print("\t- maximum: %d" % pop_spike_count_stats['max'])    
    print()

    ## store metadata
    metadata = {}
    metadata['pop_size'] = len(pop)
    metadata['time_interval'] = time_interval
    metadata['binsize'] = binsize
    metadata['function'] = sys._getframe(  ).f_code.co_name
    metadata['file'] = sys._getframe(  ).f_code.co_filename
    pop_spike_count_stats['metadata'] = metadata
    
    return pop_spike_count_stats, pop_spike_count, times[:-1]

##########################################################

## (re)create model instance
parameters = model.get_default_parameters()

model.install_nestml_module(parameters['neuron_model'])
model_instance = model.Model(parameters)
model_instance.create()

## data analysis parameters
spike_file_label = 'spikes-12502'
time_interval = (0., model_instance.pars['T'])  ## time interval for spike data analysis
binsize = model_instance.pars['dt']            ## binsize (ms) for analysis of input and population spike counts

model_characteristics = {}

## input spike statistics
model_instance.connect()
subset_size = 100
pop_post = model_instance.nodes['pop_all'][:subset_size]
pop_pre = model_instance.nodes['pop_all']
in_spike_count_stats = input_spike_count_statistics(pop_pre, pop_post, binsize, time_interval, model_instance, spike_file_label)
model_characteristics['in_spike_count_stats'] = in_spike_count_stats

## output spike statistics
### time averaged rates
pop = model_instance.nodes['pop_all']
time_averaged_firing_rate_stats = time_averaged_firing_rate_statistics(pop, time_interval, model_instance, spike_file_label)
model_characteristics['time_averaged_firing_rate_stats'] = time_averaged_firing_rate_stats

### population spike counts
pop = model_instance.nodes['pop_all']
pop_spike_count_stats, pop_spike_count, pop_spike_count_times = population_spike_count_statistics(pop,  binsize, time_interval, model_instance, spike_file_label)
model_characteristics['pop_spike_count_stats'] = pop_spike_count_stats

## save data
import json
json.dump(model_characteristics, open('%s/model_characteristics.json' % model_instance.pars['data_path'], 'w' ), indent=4)
