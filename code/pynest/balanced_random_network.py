import nest
import numpy
import matplotlib.pyplot as plt

###################################################################
## parameters

## network parameters
N=12500                   ## number of neurons
epsilon=0.1              ## connectivity
gamma=0.8                ## fraction of excitatory neurons and synapses

## neuron parameters
Vth=15.                  ## spike threshold (mV)
Vrest=0.                 ## resting potential (mV)

## synapse parameters
JE=50.                   ## weight of excitatory synapses (pA)
g=10.                    ## relative weight (JI=-g*JE) of inhibitory synapses
d=1.5                    ## spike transmission delay (ms)

## input parameters
Iext=400.                ## external DC input (pA)

## simulation parameters
T=1000.                  ## simulation time (ms)
dt=0.1                   ## simulation resolution (ms)
seed = 123               ## RNG seed
n_threads = 4            ## number of threads for simulation
                         ## (note: varying the number of threads
                         ## leads to different random-number sequences,
                         ## and, hence, to different results)

###################################################################
## derived parameters

NE=int(gamma*N)    ## number of excitatory neurons
NI=N-NE                  ## number of inhibitory neurons
K=int(epsilon*N)   ## toal in-degree
KE=int(gamma*K)    ## excitatory in-degree
KI=K-KE                  ## inhibitory in-degree
JI=-g*JE                 ## inhibitory synaptic weight

###################################
## reset and configure simulation kernel
nest.ResetKernel()
nest.SetKernelStatus({
    'resolution': dt,                 ## set simulation resolution
    'rng_seed': seed,                 ## seed for NEST internal RNGs
    'local_num_threads': n_threads,   ## number of threads
    'print_time': True,               ## enable printing of simulation progress
    })

## create and configure neuron populations
neuron_params={'I_e': Iext,
               'E_L': Vrest,
               'V_th': Vth,
               'V_reset': Vrest,
}
pop = nest.Create('iaf_psc_exp', N, neuron_params) ## overall population
pop_E = pop[:NE]                                   ## exitatory neurons
pop_I = pop[NE:]                                   ## inhibitory neurons

pop.V_m = nest.random.uniform(Vrest,Vth)           ## random initial membrane potentials

## connect network
### excitatory connections
nest.Connect(pop_E, pop,
             conn_spec = {
                 'rule': 'fixed_indegree',
                 'indegree': KE,
                 'allow_autapses': False,
                 'allow_multapses': True,
             },
             syn_spec={
                 'weight': JE,
                 'delay': d
             })
### inhibitory connections
nest.Connect(pop_I, pop,
             conn_spec = {
                 'rule': 'fixed_indegree',
                 'indegree': KI,
                 'allow_autapses': False,
                 'allow_multapses': True,
             },
             syn_spec={
                 'weight': JI,
                 'delay': d
             })

## set up and connect spike recorder
sd=nest.Create('spike_recorder')
nest.Connect(pop,sd)

## run simulation
nest.Simulate(T)

## read out recorded spikes
spike_senders=sd.get('events')['senders']
spike_times=sd.get('events')['times']

## compute average firing rate
rate=sd.get('n_events')/T*1e3/N

###################################
# plotting
plt.figure(1,dpi=300)
plt.clf()
plt.plot(spike_times,spike_senders,'ko',mec=None,markersize=1,rasterized=True,alpha=0.3)
plt.xlim(0,T)
plt.ylim(numpy.array(pop)[0],numpy.array(pop)[-1])
plt.xlabel('time (ms)')
plt.ylabel('neuron id')
plt.title('average firing rate $=%.2f\,\,\mathsf{spikes/s}$' % rate)
plt.savefig('./figures/balanced_random_network.pdf')

