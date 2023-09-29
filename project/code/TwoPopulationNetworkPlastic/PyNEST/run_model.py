import sys
import model
import psutil

#################################################
def run_model():
    '''
    Runs the model and stores data on disk (spike data and model paramaters).

    Note: Data can be loaded from file using

             parameters = model.get_default_parameters()
             spikes = model.load_spike_data('./')

    Arguments
    ---------

    Returns
    -------
    
    '''

    parameters = model.get_default_parameters()
    parameters['record_spikes'] = True
    #parameters['record_weights'] = True

    model.install_nestml_module(parameters['neuron_model'])

    model_instance = model.Model(parameters)
    model_instance.create()
    model_instance.connect()

    ## connectivity at start of simulation
    subset_size = 1000 #2000    ## number of pre- and post-synaptic neurons weights are extracted from
    pop_pre = model_instance.nodes['pop_E'][:subset_size]
    pop_post = model_instance.nodes['pop_E'][:subset_size]
    C = model_instance.get_connectivity(pop_pre, pop_post, model_instance.pars['data_path'] +  '/' +'connectivity_presim.dat')

    ## simulate
    model_instance.simulate(model_instance.pars['T'])

    ## save parameters to file
    model_instance.save_parameters('model_instance_parameters',model_instance.pars['data_path'])

    ## connectivity at end of simulation
    C = model_instance.get_connectivity(pop_pre, pop_post, model_instance.pars['data_path'] + '/' + 'connectivity_postsim.dat')
        
    return 

#################################################

run_model()


