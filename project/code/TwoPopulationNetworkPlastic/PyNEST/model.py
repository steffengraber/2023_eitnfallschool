"""
TwoPopulationNetworkPlastic

Model definition, PyNEST implementation, and associated helper functions.

Default parameters are provided in "parameter_dicts.py".

"""

import sys
import os
import numpy as np
import copy
import nest
import scipy.special

##############################################
class Model:
    """ 
    Instantiation of the TwoPopulationNetworkPlastic model and its PyNEST implementation.

    Note: Each model in the testcase repository provides the same set of member functions 

    __init__(parameters)
    create()
    connect()
    simulate(t_sim)

    In addition, each model may implement other model-specific member functions.

    """

    ##############################################
    def __init__(self, parameters):
        '''
        Intialise model and simulation instance, including

        1) parameter setting,
        2) configuration of the NEST kernel,
        3) setting random-number generator seed, and
        4) configuration of neuron and synapse models.

        Arguments
        ---------

        parameters:    dict
                       Parameter dictionary

        Returns
        -------

        '''
        
        print("\nInitialising model and simulation...")

        # set parameters derived from base parameters
        self.__derived_parameters(parameters)

        # create data directory (if necessary)
        os.system('mkdir -p ' + self.pars['data_path'])
        
        # initialize NEST kernel
        nest.ResetKernel()
        nest.SetKernelStatus({
            'tics_per_ms': 1.*self.pars['tics_per_step']/self.pars['dt'],
            'resolution': self.pars['dt'],
            'print_time': self.pars['print_simulation_progress'],
            'local_num_threads': self.pars['n_threads'],
            'rng_seed': self.pars['seed'],
            'dict_miss_is_error': True,
            'data_path': self.pars['data_path'],
            'overwrite_files': True, 
        })
        np.random.seed(self.pars['seed'])
        
        nest.set_verbosity(self.pars['nest_verbosity'])

        # configure neuron and synapse models
        if self.pars['neuron_model'] == 'iaf_psc_alpha_nest':
            self.__neuron_params = {
                'V_th': self.pars['theta'],
                'E_L': self.pars['E_L'],
                'V_reset': self.pars['V_reset'],
                'tau_m': self.pars['tau_m'],
                't_ref': self.pars['t_ref'],
                'C_m': self.pars['C_m'],
                'tau_syn_ex': self.pars['tau_s'],
                'tau_syn_in': self.pars['tau_s'],
                'I_e': self.pars['I_DC'],
                'tau_minus': self.pars['stdp_tau_minus'],
                'V_m': self.pars['V_init_min'],
            }
            
        elif self.pars['neuron_model'] == 'iaf_psc_alpha_nestml':
            self.__neuron_params = {
                'V_th': self.pars['theta'],
                'E_L': self.pars['E_L'],
                'V_reset': self.pars['V_reset'],
                'tau_m': self.pars['tau_m'],
                't_ref': self.pars['t_ref'],
                'C_m': self.pars['C_m'],
                'tau_syn_exc': self.pars['tau_s'],
                'tau_syn_inh': self.pars['tau_s'],
                'I_e': self.pars['I_DC'],
                'tau_minus': self.pars['stdp_tau_minus'],
                'V_m': self.pars['V_init_min'],                
            }
                        
    ##############################################        
    def __derived_parameters(self,parameters):
        """
        Set additional parameters derived from base parameters.

        A dictionary containing all (base and derived) parameters is stored as model attribute self.pars.

        Arguments
        ---------

        parameters:    dict
                       Dictionary containing base parameters

        """
        
        self.pars = copy.deepcopy(parameters)

        self.pars['N_E'] = int(self.pars['beta'] * self.pars['N'])  # number of excitatory neurons
        self.pars['N_I'] = self.pars['N']-self.pars['N_E']           # number of inhibitory neurons        
        self.pars['K_E'] = int(self.pars['beta'] * self.pars['K'])  # number of excitatory inputs per neuron
        self.pars['K_I'] = self.pars['K']-self.pars['K_E']           # number of inhibitory inputs per neuron

        # conversion of PSP amplitudes to PSC amplitudes
        self.pars['J_unit'] = unit_psp_amplitude(self.pars['tau_m'], self.pars['C_m'], self.pars['tau_s']) # unit PSP amplitude        
        self.pars['I_E'] = self.pars['J_E'] / self.pars['J_unit']  # EPSC amplitude for local inputs (pA)
        self.pars['I_I'] = - self.pars['g'] * self.pars['I_E']     # IPSC amplitude (pA)
        self.pars['I_X'] = self.pars['I_E']                        # EPSC amplitude for external inputs (pA)
        
        # rate of external Poissonian sources
        self.pars['nu_theta'] = 1000. * self.pars['theta'] * self.pars['C_m'] / (self.pars['I_X'] * np.exp(1.) * self.pars['tau_m'] * self.pars['tau_s'])
        self.pars['nu_X'] = self.pars['eta'] * self.pars['nu_theta']

        # number of neurons spikes are recorded from
        if self.pars['N_rec_spikes'] == 'all':
            self.pars['N_rec_spikes'] = self.pars['N']

        return

    ##############################################                
    def create(self):
        '''
        Create and configure all network nodes (neurons + recording and stimulus devices), incl. setting of initial conditions.

        A dictionary containing all node IDs is stored as model attribute self.nodes.

        '''
        print("\nCreating and configuring nodes...")
        
        # create neuron populations
        if self.pars['neuron_model'] == 'iaf_psc_alpha_nest': 
            pop_all = nest.Create('iaf_psc_alpha', self.pars['N'], self.__neuron_params) # overall population
        elif self.pars['neuron_model'] ==  'iaf_psc_alpha_nestml':
            pop_all = nest.Create('iaf_psc_alpha_nestml__with_stdp_pl_nestml', self.pars['N'], self.__neuron_params) # overall population

        # set random initial membrane potentials
        if self.pars['neuron_model'] == 'iaf_psc_alpha_nest':
            random_vm = nest.random.uniform(self.pars['V_init_min'],self.pars['V_init_max'])                    
            nest.GetLocalNodeCollection(pop_all).V_m = random_vm                    

        elif self.pars['neuron_model'] == 'iaf_psc_alpha_nestml':             
            random_vm = np.random.uniform(low = self.pars['V_init_min'],high = self.pars['V_init_max'],size=self.pars['N'])
            pop_all.V_m = random_vm                                                                                                            
        pop_E = pop_all[:self.pars['N_E']]    # population of exitatory neurons
        pop_I = pop_all[self.pars['N_E']:]    # population of inhibitory neurons

        # create external Poissonian sources (stimulus)
        poisson = nest.Create('poisson_generator', params = {'rate': self.pars['nu_X']})

        # create recording devices
        if self.pars['record_spikes']:
            # create, configure and connect spike detectors
            spike_recorder = nest.Create('spike_recorder', {'record_to': 'ascii', 'label': 'spikes'})
        else:
            spike_recorder = None

        # if self.pars['record_weights']:
        #     # create, configure and connect weight recorder
        #     weight_recorder = nest.Create('weight_recorder', {
        #         'start': self.pars['weight_recording_start_time'],
        #         'record_to': 'ascii',
        #         'label': 'weights'
        #     })
        # else:
        #     weight_recorder = None

        # configure connections
        if self.pars['neuron_model'] == 'iaf_psc_alpha_nest': 
            nest.CopyModel("stdp_pl_synapse_hom_hpc", "excitatory_plastic", {
                "weight": self.pars['I_E'],
                "delay": self.pars['delay'],
                'alpha': self.pars['stdp_alpha'],
                'lambda': self.pars['stdp_lambda'],
                'mu': self.pars['stdp_mu_plus'],
                'tau_plus': self.pars['stdp_tau_plus'],
            })

        elif self.pars['neuron_model'] == 'iaf_psc_alpha_nestml': 
            nest.CopyModel('stdp_pl_nestml__with_iaf_psc_alpha_nestml',"excitatory_plastic", {
                #'weight_recorder': weight_recorder[0],
                'weight': self.pars['I_E'],
                'w_0': self.pars['stdp_w_0'],                
                'lambda': self.pars['stdp_lambda'],
                'alpha': self.pars['stdp_alpha'],
                'tau_plus': self.pars['stdp_tau_plus'],
                'tau_minus': self.pars['stdp_tau_minus'],
                'the_delay': self.pars['delay'],
                'mu_plus': self.pars['stdp_mu_plus'],
                'receptor_type': 0
            })
            
        # if self.pars['record_weights']:
        #     nest.SetDefaults('excitatory_plastic',{'weight_recorder': weight_recorder})
            
        nest.CopyModel("static_synapse_hpc", "excitatory_static", {
            "weight": self.pars['I_E'],
            "delay": self.pars['delay']
        })
        nest.CopyModel("static_synapse_hpc", "inhibitory", {
            "weight": self.pars['I_I'],
            "delay": self.pars['delay']
        })
        nest.CopyModel("static_synapse_hpc", "external", {
            "weight": self.pars['I_X'],
            "delay": self.pars['delay']
        })

        # store nodes in model instance
        self.nodes = {}
        self.nodes['pop_all'] = pop_all
        self.nodes['pop_E'] = pop_E
        self.nodes['pop_I'] = pop_I
        self.nodes['poisson'] = poisson
        self.nodes['spike_recorder'] = spike_recorder
        #self.nodes['weight_recorder'] = weight_recorder        

        return
    
    ##############################################                
    def connect(self):
        '''
        Connect network and devices.

        '''
        
        print("\nConnecting network and devices...")
        ## fetch neuron populations and device ids
        pop_all = self.nodes['pop_all']
        pop_E = self.nodes['pop_E']
        pop_I = self.nodes['pop_I']
        poisson = self.nodes['poisson']
        spike_recorder = self.nodes['spike_recorder']

        # connect network
        ## EE connections (plastic)
        nest.Connect(pop_E, pop_E, conn_spec = {
            'rule': 'fixed_indegree',
            'indegree': self.pars['K_E'],
            'allow_autapses': self.pars['allow_autapses'],
            'allow_multapses': self.pars['allow_multapses'],
        }, syn_spec="excitatory_plastic")

        ## EI connections (static)
        nest.Connect(pop_E, pop_I, conn_spec = {
            'rule': 'fixed_indegree',
            'indegree': self.pars['K_E'],
            'allow_autapses': False,
            'allow_multapses': True,
        }, syn_spec="excitatory_static")

        ## IE and II connections (static)
        nest.Connect(pop_I, pop_all, conn_spec = {
            'rule': 'fixed_indegree',
            'indegree': self.pars['K_I'],
            'allow_autapses': self.pars['allow_autapses'],
            'allow_multapses': self.pars['allow_multapses'],
        }, syn_spec="inhibitory")

        # connect external Poissonian sources (stimulus)
        nest.Connect(poisson, pop_all, syn_spec ="external")
        
        # connect recording devices (to the first N_rec_spikes neurons)
        if self.pars['record_spikes']:
            nest.Connect(pop_all[:self.pars['N_rec_spikes']], spike_recorder)

        '''
        Since the introduction of the 5g kernel in NEST 2.16.0 
        the full connection infrastructure, including presynaptic connectivity, 
        is set up in the preparation phase of the simulation.
        The preparation phase is usually induced by the first
        "nest.Simulate()" call. For including this phase in measurements of the 
        connection time, we induce it here explicitly by calling ``nest.Prepare()``.            
        '''    
        nest.Prepare()
        nest.Cleanup()

        return

    ##############################################                        
    def simulate(self, t_sim):
        '''
        Run simulation.

        Arguments
        ---------
        t_sim: float
               Simulation time (ms).
    
        '''
    
        print("\nSimulating...")
    
        nest.Simulate(t_sim)

        return

    ##############################################
    def save_parameters(self,filename_root,path):
        '''
        Save model-instance parameters to file.

        Arguments
        ---------
        filename_root: str
                       Root of file name.
                       
        path:          str
                       File path
                       
        '''

        
        import json    
        json.dump(self.pars, open('%s/%s.json' % (path,filename_root), 'w' ), indent=4)
        
        return        

    ##############################################
    def get_connectivity(self,pop_pre, pop_post, filename=None):
        '''
        Extract connectivity for subpopulations pop_pre and pop_post and store in file filename (unless filename=None [default]).

        Arguments
        ---------
        pop_pre:        NodeCollection
                        Presynaptic neuron population.

        pop_post:       NodeCollection
                        Postsynaptic neuron population.

        filename:       str
                        Name of file to store connectivity data. If filename ends in ".gz", 
                        the file will be compressed in gzip format. Set filename=None (default) 
                        to prevent storage on disk.

        Returns
        -------
        C:        numpy.ndarray
                  Lx4 array containing connectivity information:

                     C[:,0]: source id
                     C[:,1]: target id
                     C[:,2]: synaptic weight
                     C[:,3]: delay (ms)

                  (L = len(pop_pre)*len(pop_post) = number of connections.

        '''
        print('Extracting connectivity...')
        
        conns = nest.GetConnections(source=pop_pre,target=pop_post)
        
        C = np.zeros((len(conns),4))
        C[:,0] = conns.get()['source']
        C[:,1] = conns.get()['target']
        C[:,2] = conns.get()['weight']
        C[:,3] = conns.get()['delay']

        if filename:
            np.savetxt(filename,C,fmt='%d\t%d\t%.3e\t%.3e',header=' source \t target \t weight \tdelay (ms)')

        return C
    
##############################################        
##############################################
def install_nestml_module(neuron_model):
    '''Install NESML module depending on neuron model.'''

    if neuron_model == 'iaf_psc_alpha_nest':
        pass
    elif neuron_model == 'iaf_psc_alpha_nestml':
        nest.Install('nestmlmodule') ## include nestml models
    return

##############################################
def get_default_parameters():
    '''    
    Import default model-parameter file.

    Returns
    -------
    pars: dict
          Parameter dictionary.

    '''

    import parameter_dicts
    pars = parameter_dicts.pars
    
    return pars


##############################################
def get_data_file_list(path, label):
    '''
    Searches for files with extension "*.dat" in directory "path" with names starting with "label", 
    and returns list of file names.

    Arguments
    ---------
    path:           str
                    Path containing spike files.

    label:          str
                    Spike file label (file name root).

    Returns
    -------
    files:          list(str)
                    List of file names


    '''
 
    ## get list of files names
    files = []
    for file_name in os.listdir(path):
        if file_name.endswith('.dat') and file_name.startswith(label):
            files += [file_name]
    files.sort()
    
    assert len(files)>0 ,'No files of type "%s*.dat" found in path "%s".' % (label,path)

    return files

##############################################
#def load_spike_data(path, label, skip_rows = 3):
def load_spike_data(path, label, time_interval = None, pop = None, skip_rows = 3):        
    '''
    Load spike data from files.

    Arguments
    ---------
    path:           str
                    Path containing spike files.

    label:          str
                    Spike file label (file name root).

    time_interval:  None (default) or tuple (optional)
                    Start and stop of observation interval (ms). All spikes outside this interva are discarded.
                    If None, all recorded spikes are loaded.

    pop:            None (default) or nest.NodeCollection (optional)
                    Oberserved neuron population. All spike sendes that are not part of this population are discarded.
                    If None, all recorded spikes are loaded.

    skip_rows:      int (optional)
                    Number of rows to be skipped while reading spike files (to remove file headers). The default is 3.

    Returns
    -------
    spikes:   numpy.ndarray
              Lx2 array of spike senders spikes[:,0] and spike times spikes[:,1] (L = number of spikes).

    '''

    if type(time_interval) == tuple:
        print('Loading spike data in interval (%.1f ms, %.1f ms] ...' % (time_interval[0], time_interval[1]) )
    else:
        print('Loading spike data...')        

    files = get_data_file_list(path, label)
    
    ## open spike files and read data
    spikes = []
    for file_name in files:
        try:
            spikes += [np.loadtxt('%s/%s' % (path,file_name),skiprows=skip_rows)] ## load spike file while skipping the header 
        except:
            print('Error: %s' % sys.exc_info()[1])
            print('Remove non-numeric entries from file %s (e.g. in file header) by specifying (optional) parameter "skip_rows".\n' % (file_name))
            
    spikes = np.concatenate(spikes)

    ## extract spikes in specified time interval
    if time_interval != None:
        if type(time_interval) == tuple:
            ind = (spikes[:,1]>=time_interval[0]) * (spikes[:,1]<=time_interval[1]) 
            spikes = spikes[ind,:]
        else:
            print("Warning: time_interval must be a tuple or None. All spikes are loaded.")

    if type(pop) == nest.NodeCollection:
        spikes_subset = []
        for cn,nid in enumerate(pop):  ## loop over all neurons
            print("Spike extraction from %d/%d (%d%%) neurons completed" % (cn+1, len(pop), 1.*(cn+1)/len(pop)*100), end = '\r')            
            ind = np.where(spikes[:,0] == nid)[0]
            spikes_subset += list(spikes[ind,:])
        spikes = np.array(spikes_subset)
    elif pop == None:
        pass
    else:
        print("Warning: pop must be a NEST NodeCollection or None. All spikes are loaded.")
    print()
    
    return spikes

##############################################
def load_connectivity_data(path, label, skip_rows = 1):    
    '''
    Load connectivity data (weights and delays) from files.

    Arguments
    ---------
    path:           str
                    Path containing connectivity files.

    label:          str
                    Connectivity file label (file name root).

    skip_rows:      int, optional
                    Number of rows to be skipped while reading connectivity files (to remove file headers). The default is 1.

    Returns
    -------
    C:        numpy.ndarray
              Lx4 array containing connectivity information:

                 C[:,0]: source id
                 C[:,1]: target id
                 C[:,2]: synaptic weight
                 C[:,3]: delay (ms)
              
              (L = len(pop_pre)*len(pop_post) = number of connections.

    '''

    files = get_data_file_list(path, label)

    ## open weight files and read data
    C = []
    for file_name in files:
        try:
            C += [np.loadtxt('%s/%s' % (path,file_name),skiprows=skip_rows)] ## load file while skipping the header 
        except:
            print('Error: %s' % sys.exc_info()[1])
            print('Remove non-numeric entries from file %s (e.g. in file header) by specifying (optional) parameter "skip_rows".\n' % (file_name))
            
    C = np.concatenate(C)
    
    return C

##############################################
# def load_weight_data(path, label, skip_rows = 3):    
#     '''
#     Load synaptic-weight data from files.

#     Arguments
#     ---------
#     path:           str
#                     Path containing weight files.

#     label:          str
#                     Weight file label (file name root).

#     skip_rows:      int, optional
#                     Number of rows to be skipped while reading weight files (to remove file headers). The default is 3.

#     Returns
#     -------
#     weights:   numpy.ndarray
#               Lx4 array
#               weights[:,0]: spike senders 
#               weights[:,1]: spike times
#               weights[:,2]: synaptic weight
#               weights[:,3]: spike target
#               (L = number of recorded weights.

#     '''

#     files = get_data_file_list(path, label)

#     ## open weight files and read data
#     weights = []
#     for file_name in files:
#         try:
#             weights += [np.loadtxt('%s/%s' % (path,file_name),skiprows=skip_rows)] ## load spike file while skipping the header 
#         except:
#             print('Error: %s' % sys.exc_info()[1])
#             print('Remove non-numeric entries from file %s (e.g. in file header) by specifying (optional) parameter "skip_rows".\n' % (file_name))
            
#     weights = np.concatenate(weights)
    
#     return weights

##############################################

def unit_psp_amplitude(tau_m, C_m, tau_s):
    '''
    Compute PSP maximum (mV) for LIF with alpha-shaped PSCs with unit amplitude 1.

    Arguments
    ---------
    tau_m:  float
            Membrane time constant (ms).

    C_m:    float
            Membrane capacitance (pF).

    tau_s:  float
            Synaptic time constant (ms).


    Returns
    -------
    J_unit: float
            Unit-PSP amplitude (mV).

    '''

    a = tau_s / tau_m
    b = 1.0 / tau_s - 1.0 / tau_m

    # time of PSP maximum
    t_max = 1.0 / b * (-LambertWm1(-a * np.exp(a)) - a)

    J_unit = np.exp(1.0) / C_m / (1. - tau_s/tau_m) * \
        ( (np.exp(-t_max/tau_m) - np.exp(-t_max/tau_s)) / b - \
          t_max * np.exp(-t_max/tau_s))
       
    return J_unit

##############################################
def LambertWm1(x):
    y = scipy.special.lambertw(x,k=-1 if x < 0 else 0).real

    return y

##############################################
def get_index(x,y):
    '''
    Return indices of x where x==y.

    Arguments
    ---------
    x: list or numpy.ndarray of int, float, str

    y: int, float, str

    Returns
    -------
    ind: numpy.ndarray
         Index array

    '''
    return np.where(x==y)[0]
    
##############################################
def get_connectivity_matrix(connectivity, pop_pre = [], pop_post = []):    
    '''
    Generate connectivity matrix from connectivity data in 'connectivity' 
    for the (sub-)set of source and target neurons in 'pop_pre' and 'pop_post'.
    If 'pop_pre' or 'pop_post' are empty (default), the arrays of source and 
    target neurons will be constructed from "connectivity".

    Arguments
    ---------
    connectivity: numpy.ndarray
                  Lx4 array containing connectivity information:

                     connectivity[:,0]: source id
                     connectivity[:,1]: target id
                     connectivity[:,2]: synaptic weight
                     connectivity[:,3]: delay (ms)
              
                  (L = len(pop_pre)*len(pop_post) = number of connections

    pop_pre:  numpy.ndarray
              Array of source ids (default: [])

    pop_post: numpy.ndarray
              Array of target ids (default: [])

    Returns
    -------
    W:        numpy.ndarray
              Connectivity matrix of shape LTxLS, with number of targets LT and number of sources LS

    '''

    print('\nGenerating connectivity matrix...')

    if len(pop_pre)==0:
        pop_pre = np.unique(connectivity[:,0])
    if len(pop_post)==0:
        pop_post = np.unique(connectivity[:,1])
    
    ## initialise weight matrix
    W = np.zeros([len(pop_post),len(pop_pre)]) ## convention: pre = columns, post = rows
    
    ## fill weight matrix
    for c in range(connectivity.shape[0]):
        W[get_index(pop_post,connectivity[c,1]),get_index(pop_pre,connectivity[c,0])] = connectivity[c,2]
    
    return W, pop_pre, pop_post

##############################################
def get_weight_distribution(connectivity,weights):
    return np.histogram(connectivity[:,2],weights,density=True)[0]

##############################################
