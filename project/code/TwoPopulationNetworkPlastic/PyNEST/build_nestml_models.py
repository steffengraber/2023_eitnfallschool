import nest
from pynestml.frontend.pynestml_frontend import generate_nest_target

#################################################
## create nest models from nestml

path_to_nestml_models = '../nestml_models'

# def install_nestml_module():
#     input_path = [path_to_nestml_models + "/iaf_psc_alpha.nestml"
#     ]

#     target_path = "./nestml_target"
      
#     generate_nest_target(input_path=input_path,
#                          target_path=target_path,
#                          logging_level='ERROR',
#                          suffix="_nestml",
#     )    

def install_nestml_module():
    input_path = [path_to_nestml_models + "/iaf_psc_alpha.nestml",
                  path_to_nestml_models + "/stdp_pl_synapse.nestml"
    ]

    target_path = "./nestml_target"
      
    generate_nest_target(input_path=input_path,
                         target_path=target_path,
                         logging_level='ERROR',
                         suffix="_nestml",
                         codegen_opts = {"neuron_synapse_pairs": [{"neuron": "iaf_psc_alpha",
                                                                   "synapse": "stdp_pl",
                                                                   "post_ports": ["post_spikes"]}]}
    )    
    
#################################################

install_nestml_module()
