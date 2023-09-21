import nest
from pynestml.frontend.pynestml_frontend import generate_nest_target
import matplotlib.pyplot as plt

compile_nestml_code = True
#compile_nestml_code = False

install_nestml_module = True

neuron_model_name = "iaf_psc_exp_nestml"
nestml_model_path = '../'

T = 400.                         ## simulation time (ms)
exc_stim_times = [100.]          ## times of excitatory input spikes (ms)
inh_stim_times = [200.]          ## times of inhibitory input spikes (ms)

#################################################
def create_nestml_module(neuron_model_name):
    '''
    Create nest model from nestml code.
    '''
    
    input_path = nestml_model_path + neuron_model_name + ".nestml"    
    target_path = "./nestml_target"
    
    generate_nest_target(input_path=input_path,
                    target_path=target_path,
                    logging_level='ERROR')

#################################################

if compile_nestml_code:
    create_nestml_module(neuron_model_name)

if install_nestml_module:    
    nest.Install("nestmlmodule")

#################################################    

nest.ResetKernel()

sgExc = nest.Create("spike_generator", {'spike_times': exc_stim_times})
sgInh = nest.Create("spike_generator", {'spike_times': inh_stim_times})

nrn = nest.Create(neuron_model_name, 1)
print(nest.GetStatus(nrn))

## error:
#nest.Connect(sgExc, nrn, syn_spec = {'receptor_type': 1, 'weight': 1.0, 'delay': 1.0})
#nest.Connect(sgInh, nrn, syn_spec = {'receptor_type': 2, 'weight': -1.0, 'delay': 1.0}) ## error

nest.Connect(sgExc, nrn, syn_spec = {'weight': 1.0, 'delay': 1.0})
nest.Connect(sgInh, nrn, syn_spec = {'weight': -1.0, 'delay': 1.0})

mm = nest.Create("multimeter",{"record_from": ['V_m']})
nest.Connect(mm,nrn)

nest.Simulate(T)

rec = nest.GetStatus(mm)[0]['events']

plt.figure()
plt.clf()
plt.plot(rec['times'],rec['V_m'],'k-')
plt.xlabel(r'time (ms)')
plt.ylabel(r'potential (mV)')

plt.savefig(neuron_model_name + '_test.png')
