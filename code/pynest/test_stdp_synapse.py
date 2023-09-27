import nest                                                          # import NEST module
import matplotlib.pyplot as plt                                      # for plotting
from pynestml.frontend.pynestml_frontend import generate_nest_target # NESTML
import numpy

def compile_nestml_code():
    generate_nest_target(input_path=["../nestml/iaf_psc_exp.nestml",
                                     "../nestml/stdp_synapse.nestml"],
                         target_path="./nestml_target",
                         logging_level='ERROR',
                         suffix="_nestml",
                         codegen_opts = {"neuron_synapse_pairs": [{"neuron": "iaf_psc_exp",
                                                                   "synapse": "stdp",
                                                                   "post_ports": ["post_spikes"]}]}
    )    

compile_nestml_code()

# install resulting NESTML module to make models available in NEST
nest.Install('nestmlmodule') 

# after this, the following two models are available in NEST
neuron_model_name = 'iaf_psc_exp_nestml__with_stdp_nestml'
synapse_model_name = 'stdp_nestml__with_iaf_psc_exp_nestml'

nest.ResetKernel() # reset simulation kernel

# presynaptic  spike times
pre_spike_times =  [100. , 300., 400., 500., 600., 700., 800., 900., 1000., 1200.]
# times of postsynaptic stimulation
post_spike_times = [       330., 430., 530., 630., 730., 830., 930., 1030.]

pre_neuron=nest.Create('parrot_neuron') # create presynaptic neuron
post_neuron=nest.Create(neuron_model_name) # create postsynaptic neuron

# configure STDP synapse
nest.CopyModel(synapse_model_name,"plastic_synapse", {
    "weight":     -100.0,   # initial synaptic weight (pA; >0 for excitatory and <0 for inhibitory synapses)
    "delay":         0.1,   # spike transmission delay (ms)
    'lambda':        5.0,   # (dimensionless) learning rate for causal updates
    'alpha':         0.0,   # relative learning rate for acausal firing
    'tau_tr_pre':   10.0,   # time constant of presynaptic trace (ms)
    'tau_tr_post':  10.0,   # time constant of postsynaptic trace (ms)
    'mu_plus':       0.0,   # weight dependence exponent for causal updates
    'mu_minus':      0.0,   # weight dependence exponent for causal updates    
    'Wmax':       500.0,    # maximum absolute value of synaptic weight (pA)
    'Wmin':          0.0,   # minimum absolute value of synaptic weight (pA) 
})

# connect pre neuron and post neuron with the STDP synapse
nest.Connect(pre_neuron, post_neuron, syn_spec="plastic_synapse")

# spike generator making presynaptic neuron fire at specified times
pre_sg=nest.Create('spike_generator', params={'spike_times': pre_spike_times})

# spike generator making presynaptic neuron fire at specified times
post_sg=nest.Create('spike_generator', params={'spike_times': post_spike_times})

# connect spike generators to neurons
nest.Connect(pre_sg, pre_neuron, syn_spec = {"delay": 0.1})
nest.Connect(post_sg, post_neuron, syn_spec = {"delay": 0.1, "weight": 1700.})

# create multimeter and set it up to record the membrane potential V_m
multimeter=nest.Create('multimeter',{'record_from': ['V_m'], 'interval': 0.1})

nest.Connect(multimeter, post_neuron)  # connect multimeter to the neuron

# get weight before simulation
weight_pre_sim = nest.GetConnections(pre_neuron,post_neuron).get('weight')

nest.Simulate(1400.) # run simulation

# get weight after simulation
weight_post_sim = nest.GetConnections(pre_neuron,post_neuron).get('weight')

print("\nweight (pre sim) = %.2fpA\nweight (post sim) = %.2fpA" % (weight_pre_sim,weight_post_sim))

# read out recording time and voltage from voltmeter
times=multimeter.get('events')['times']
voltage=multimeter.get('events')['V_m']

# plot results
plt.figure(1)
plt.clf()
plt.plot(pre_spike_times,len(pre_spike_times)*[17.]  ,'b|',ms=12,label='pre spikes')
plt.plot(post_spike_times,len(post_spike_times)*[16.],'r|',ms=12,label='post stimulus')
plt.plot(times,voltage,'k-',lw=2,label='membrane potential')
plt.hlines(15,0,1600,color='0.6',lw=1,ls='--',label='threshold')
plt.legend(loc=3,framealpha=1.)
plt.xlabel('time (ms)')
plt.ylabel('membrane potential (mV)')
plt.xlim(0,1400)
plt.ylim(-10,18)
plt.savefig('./figures/std_synapse_test.pdf')
