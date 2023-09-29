## default parameters for TwoPopulationNetworkPlastic

pars = {}

pars['model_name'] = 'TwoPopulationNetworkPlastic'  # model name

# network and connectivity parameters
pars['N'] = 12500          # total number of neurons 
pars['K'] = 1250           # total number of inputs per neuron from local network
pars['beta'] = 0.8         # fraction of excitatory neurons/inputs

pars['allow_autapses'] = False
pars['allow_multapses'] = True

# neuron parameters
pars['neuron_model'] = 'iaf_psc_alpha_nest'    # NEST version of iaf_psc_alpha and stdp_pl_synapse

#pars['neuron_model'] = 'iaf_psc_alpha_nestml' # NESTML version of iaf_psc_alpha and stdp_pl_synapse
## note: to build the NESTML models, run build_nestml_models.py first

pars['E_L'] = 0.0      # resting membrane potential(mV)
pars['C_m'] = 250.0    # membrane capacity (pF)
pars['tau_m'] = 20.0   # membrane time constant (ms)
pars['t_ref'] = 2.     # duration of refractory period (ms)
pars['theta'] = 20.0   # spike threshold(mV)
pars['V_reset'] = 0.0  # reset potential(mV)
    
# stimulus parameters
pars['I_DC'] = 0.0     # (constant) external input current (pA)
pars['eta'] = 1.2      # rate of external Poissonian sources relative to threshold rate

# synapse parameters
pars['J_E'] = 0.5      # EPSP amplitude (mV)
pars['g'] = 10.0       # relative IPSP amplitude (JI=-g*JE)
pars['delay'] = 1.5    # spike transmission delay (ms)
pars['tau_s'] = 2.0    # synaptic time constant (ms)

pars['stdp_alpha'] = 0.1   # relative magnitude of weight update for acausal firing

## slightly reducing alpha leads to an unstable dynamics:
#pars['stdp_alpha'] = 0.05 #0.05  # relative magnitude of weight update for acausal firing

pars['stdp_lambda'] = 20.        # magnitude of weight update for causal firing
pars['stdp_mu_plus'] = 0.4       # weight dependence exponent for causal firing
pars['stdp_tau_plus'] = 15.0     # time constant of weight update for causal firing (ms)
pars['stdp_tau_minus'] = 30.0    # time constant of weight update for acausal firing (ms)
pars['stdp_w_0'] = 1.0            # reference weight (pA)

# initial conditions
pars['V_init_min'] = pars['E_L']    # min of initial membrane potential (mV)
pars['V_init_max'] = pars['theta']  # min of initial membrane potential (mV)

# data recording
pars['record_spikes'] = False   # if True: set up spike detectors and record spikes
pars['N_rec_spikes'] = 'all'    # number of neurons to record spikes from; if 'all', spikes from all neurons are recorded

# pars['record_weights'] = False           # True: record weights of plastic synapses
# pars['weight_recording_start_time'] = 0. # start time of weight recording (ms)

# simulation parameters
pars['T'] = 10000.            # simulation time
pars['dt'] = 2**-3            # simulation resolution (ms)  !!! revise documentation (incl delay)
pars['tics_per_step'] = 2**7  # number of tics per time step (defines resolution of time variables in NEST)
pars['seed'] = 1              # seed for random number generator
pars['n_threads'] = 4         # number of threads for simulation
                              # (note: varying the number of threads leads to different random-number sequences,
                              # and, hence, to different results)

pars['print_simulation_progress'] = True   # print network time and realtime factor
pars['nest_verbosity'] = 'M_WARNING'       # 'M_FATAL', 'M_ERROR', 'M_WARNING', 'M_DEPRECATED', 'M_INFO', 'M_ALL'

pars['data_path'] = "./data/" + pars['neuron_model']
