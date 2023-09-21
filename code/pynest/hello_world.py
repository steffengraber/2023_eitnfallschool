import nest    # import NEST module
import matplotlib.pyplot as plt # for plotting

nest.ResetKernel() # reset simulation kernel 

neuron=nest.Create('iaf_psc_exp') # create LIF neuron with exponential synaptic currents

# create a spike generator, and set it up to create two spikes at 10 and 30ms
spikegenerator=nest.Create('spike_generator', params={'spike_times': [10.,30.]}) 

# create multimeter and set it up to record the membrane potential V_m
multimeter=nest.Create('multimeter', {'record_from': ['V_m']})

# connect spike generator with neuron with synaptic weight 100 pA
nest.Connect(spikegenerator, neuron,syn_spec={'weight': 50.0})

nest.Connect(multimeter, neuron)  # connect multimeter to the neuron

nest.Simulate(100.) # run simulation for 100ms

# read out recording time and voltage from voltmeter
times=multimeter.get('events')['times']
voltage=multimeter.get('events')['V_m']

# plot results
plt.figure(1)
plt.clf()
plt.plot(times,voltage,'k-',lw=2)
plt.xlabel('time (ms)')
plt.ylabel('membrane potential (mV)')
plt.savefig('./figures/hello_world.pdf')
