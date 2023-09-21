import sys
sys.path.append(r'../')
import model

import matplotlib.pyplot as plt
from matplotlib import gridspec
import nest
import numpy as np
import os

##############################################
def time_and_population_averaged_spike_rate(spikes,time_interval,pop_size):    

    D = time_interval[1]-time_interval[0]
    n_events = sum( (spikes[:,1]>=time_interval[0]) * (spikes[:,1]<=time_interval[1]))    
    rate = n_events / D * 1000.0 / pop_size 
    print("\n-----> average firing rate: nu=%.2f /s\n" % (rate))
    return rate

#################################################
def plot_spikes(spikes, nodes, pars, path = './'):
    '''
    Create raster plot of spiking activity.
    '''

    pop_all = np.array(nodes['pop_all'])
    
    rate = time_and_population_averaged_spike_rate(spikes,(0.,pars['T']),pars['N_rec_spikes'])
    
    # plot spiking activity
    plt.figure(num=1,figsize=(7, 5))
    plt.clf()
    plt.title(r'time and population averaged firing rate: $\nu=%.2f$ spikes/s' % rate)
    plt.plot(spikes[:,1],spikes[:,0],'o',ms=0.5,lw=0, mfc='k',mec='k',alpha=0.3,rasterized=True)

    plt.xlim(0,pars['T'])
    plt.ylim(0,pars['N_rec_spikes'])
    plt.xlabel(r'time (ms)')
    plt.ylabel(r'neuron id')
    plt.savefig(path + '/TwoPopulationNetworkPlastic_spikes.png')

#################################################
# def center_axes_ticks(ax):
#     '''
#     Shift axes ticks in matrix plots to the center of each box.
#     '''
#     xticks = ax.get_xticks()
#     dx=(xticks[1]-xticks[0])/2.
#     ax.set_xticks(xticks+dx)
#     ax.set_xticklabels(xticks.astype('int'))

#     yticks = ax.get_yticks()
#     dy=(yticks[1]-yticks[0])/2.
#     ax.set_yticks(yticks+dy)
#     ax.set_yticklabels(yticks.astype('int'))

#################################################        
def plot_connectivity_matrix(W, pop_pre, pop_post, filename_label = None, path = './'):
    '''
    Plot connectivity matrix 'W' for source and target neurons contained in 'pop_pre' and 'pop_post', 
    and save figure to file.
    '''

    wmin=0
    wmax=150
    
    print('\nPlotting connectivity matrix...')
    fig = plt.figure(num=2,figsize=(6, 5))
    plt.clf()
    gs = gridspec.GridSpec(1,2, width_ratios=[15,1])

    ###

    matrix_ax = fig.add_subplot(gs[0])
    cmap = plt.cm.gray_r
    matrix = plt.pcolor(pop_pre,pop_post,W,cmap=cmap,rasterized=True,vmin=wmin,vmax=wmax)
    plt.xlabel(r'source id')
    plt.ylabel(r'target id')

    #center_axes_ticks(matrix_ax)

    plt.xlim(pop_pre[0],pop_pre[-1])
    plt.ylim(pop_post[0],pop_post[-1])
    
    ###

    cb_ax=plt.subplot(gs[1])
    cb=plt.colorbar(matrix,cax=cb_ax,extend='max')
    cb.set_label(r'synaptic weight (pA)')

    ###

    plt.subplots_adjust(left=0.12,bottom=0.1,right=0.9,top=0.95,wspace=0.1)
    plt.savefig(path + '/TwoPopulationNetworkPlastic_connectivity%s.png' % (filename_label))

#################################################
def plot_weight_distributions(whist_presim, whist_postsim, weights, path = './'):
    '''
    Plot distributions of synaptic weights before and after simulation.
    '''
    print('\nPlotting weight distributions...')
    fig = plt.figure(num=3,figsize=(6, 4))
    plt.clf()
    lw=3
    clr=['0.6','0.0']
    plt.plot(weights[:-1],whist_presim,lw=lw,color=clr[0],label=r'pre sim.')
    plt.plot(weights[:-1],whist_postsim,lw=lw,color=clr[1],label=r'post sim.')
    #plt.setp(plt.gca(),xscale='log')
    plt.setp(plt.gca(),yscale='log')    
    plt.legend(loc=1)
    plt.xlabel(r'synaptic weight (pA)')
    plt.ylabel(r'rel. frequency')
    plt.xlim(weights[0],weights[-2])
    plt.ylim(5e-5,3)        
    plt.subplots_adjust(left=0.12,bottom=0.12,right=0.95,top=0.95)
    plt.savefig(path + '/TwoPopulationNetworkPlastic_weight_distributions.png')

#################################################
def generate_reference_figures():
    '''Generate and store set of reference data'''

    ## raster plot
    parameters = model.get_default_parameters()
    parameters['record_spikes'] = True
    parameters['record_weights'] = True

    model.install_nestml_module(parameters['neuron_model'])
    
    ## fetch node ids
    model_instance = model.Model(parameters)
    model_instance.create()

    ## create subfolder for figures (if necessary)
    os.system('mkdir -p ' + model_instance.pars['data_path'])
    
    ## load spikes from reference data
    spikes = model.load_spike_data('../reference_data/' + model_instance.pars['data_path'], "spikes-%d" % (np.array(model_instance.nodes['spike_recorder'])[0]))    
    plot_spikes(spikes, model_instance.nodes, model_instance.pars, model_instance.pars['data_path'])

    ## load connectivity from reference data 
    connectivity_presim = model.load_connectivity_data('../reference_data/'+ model_instance.pars['data_path'],'connectivity_presim')
    connectivity_postsim = model.load_connectivity_data('../reference_data/' + model_instance.pars['data_path'],'connectivity_postsim')

    ## create connectivity matrices before and after simulation for a subset of neurons
    subset_size = 100
    pop_pre = np.array(model_instance.nodes['pop_E'])[:subset_size]
    pop_post = np.array(model_instance.nodes['pop_E'])[:subset_size]
    W_presim, pop_pre, pop_post = model.get_connectivity_matrix(connectivity_presim, pop_pre, pop_post)
    W_postsim, pop_pre, pop_post = model.get_connectivity_matrix(connectivity_postsim, pop_pre, pop_post)
    
    ## plot connectivity matrices
    plot_connectivity_matrix(W_presim, pop_pre, pop_post,'_presim', model_instance.pars['data_path'])
    plot_connectivity_matrix(W_postsim, pop_pre, pop_post,'_postsim', model_instance.pars['data_path'])

    ## compute weight distributions
    #weights = np.arange(29.5,34.1,0.05)
    weights = np.arange(0.,150.1,0.5)
    whist_presim = model.get_weight_distribution(connectivity_presim,weights)
    whist_postsim = model.get_weight_distribution(connectivity_postsim,weights)

    ## plot weight distributions
    plot_weight_distributions(whist_presim, whist_postsim, weights, model_instance.pars['data_path'])
            
#################################################

generate_reference_figures()
