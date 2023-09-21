import nest                                                          # import NEST module
import matplotlib.pyplot as plt                                      # for plotting
from pynestml.frontend.pynestml_frontend import generate_nest_target # NESTML
import numpy

# compile nestml model (needs to be done only once)
# generate_nest_target(input_path=["../nestml/iaf_psc_exp.nestml",
#                                  "../nestml/stdp_pl_synapse.nestml"],
#                      target_path="./nestml_target",
#                      logging_level='ERROR',
#                      suffix="_nestml",
#                      codegen_opts = {"neuron_synapse_pairs": [{"neuron": "iaf_psc_exp",
#                                                                "synapse": "stdp_pl",
#                                                                "post_ports": ["post_spikes"]}]}
# )    

# install resulting NESTML module to make models available in NEST
nest.Install('nestmlmodule') 

# after this, the following two models are available in NEST
neuron_model_name = 'iaf_psc_exp_nestml__with_stdp_pl_nestml'
synapse_model_name = 'stdp_pl_nestml__with_iaf_psc_exp_nestml'

nest.ResetKernel() # reset simulation kernel 

# list of pre and postsynaptic psike times
pre_spike_times = numpy.arange(200.,1000.,100.)
post_spike_times = pre_spike_times + 50.
pre_spike_times = [10.] + list(pre_spike_times) + [1100., 1150.]

# create a spike generator emulating the presynaptic neuron
pre_neuron=nest.Create('spike_generator', params={'spike_times': pre_spike_times}) 

post_neuron=nest.Create(neuron_model_name,2) # create postsyptic neuron

# connect the pre neuron and the post neuron with the STDP synapse
nest.CopyModel(synapse_model_name,"excitatory", {
    "weight": 100.0,      ## initial synaptic weight (pA)
    "delay": 1.0,         ## spike transmission delay (ms)
    'lambda': 0.1,        ## (dimensionless) learning rate
    'alpha': 0.1,         ##
    'tau_plus': 15.0,     ## (ms)
    'tau_minus': 100.0,    ## (ms)
    'mu_plus': 0.4,       ##
})
nest.Connect(pre_neuron, post_neuron, syn_spec="excitatory")

# create a second spike generator to make the postsynaptic neuron fire at specific times
spikegenerator=nest.Create('spike_generator', params={'spike_times': post_spike_times}) 

# connect this spikegenerator with the neuron (with a static synapse with high weight)
nest.Connect(spikegenerator, post_neuron, syn_spec = {"weight": 2000.})

# create multimeter and set it up to record the membrane potential V_m
multimeter=nest.Create('multimeter',
                       {'record_from': ['V_m','post_trace__for_stdp_pl_nestml']})

nest.Connect(multimeter, post_neuron)  # connect multimeter to the neuron

nest.Simulate(1200.) # run simulation

# read out recording time and voltage from voltmeter
times=multimeter.get('events')['times']
voltage=multimeter.get('events')['V_m']
post_trace=multimeter.get('events')['post_trace__for_stdp_pl_nestml']

# plot results
plt.figure(1)
plt.clf()
plt.subplot(211)
plt.plot(times,voltage,'k-',lw=2)
plt.xlabel('time (ms)')
plt.ylabel('membrane potential (mV)')

plt.subplot(212)
plt.plot(times,post_trace,'k-',lw=2)
plt.xlabel('time (ms)')
plt.ylabel('post trace ')

plt.savefig('./figures/hello_world_plastic_nestml.pdf')
