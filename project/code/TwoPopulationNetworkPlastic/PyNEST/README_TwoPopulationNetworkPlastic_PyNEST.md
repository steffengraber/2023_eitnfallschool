# TwoPopulationNetworkPlastic - PyNEST implementation

## Simulation script
The model is defined in [`model.py`](model.py) and [`parameter_dicts.py`](parameter_dicts.py), and can be run by executing [`run_model.py`](run_model.py). The resulting spike and and connectivity data is stored in the `data_path` defined in [`parameter_dicts.py`](parameter_dicts.py). The data is plotted by executing [`plot_data.py`](plot_data.py).

## Simulation details

By default, this implementation is based on the [`iaf_psc_alpha`](https://nest-simulator.readthedocs.io/en/latest/models/iaf_psc_alpha.html) neuron and the [`stdp_pl_synapse_hom`](https://nest-simulator.readthedocs.io/en/latest/models/stdp_pl_synapse_hom.html) synapse models provided in [NEST]. Alternatively, the user may choose a [NESTML] description of the dynamics (see [`iaf_psc_alpha`](../nestml_models/iaf_psc_alpha.nestml) and [`stdp_pl_synapse`](../nestml_models/stdp_pl_synapse.nestml)) by setting `pars['neuron_model']='iaf_psc_alpha_nestml'` in  `parameter_dicts.py`. To enable usage of the NESTML models, the script [```build_nestml_models.py```](./build_nestml_models.py) needs to be executed first.

The network is connected according to the [`fixed_indegree`](https://nest-simulator.readthedocs.io/en/latest/synapses/connection_management.html#fixed-indegree) connection rule in NEST.

The neuron dynamics is propagated in time using exact integration ([Rotter & Diesmann (1999)]) with a simulation step size $`\Delta{}t`$. The synapse dynamics is updated in an event-based manner as described by [Morrison et al. (2007)].

The model implementation runs with [NEST 3.5](https://github.com/nest/nest-simulator.git) and [NESTML 5.1.0](https://github.com/nest/nestml).

## Simulation parameters

| Name | Value | Description |
|--|--|--|
| $`T`$ | $`10000\,\text{ms}`$| total simulation time |
| $`\Delta{}t`$ | $`2^{-3}=0.125\,\text{ms}`$ | duration of simulation step |
| `tics_per_step` | $`2^7=128`$ | number of tics per simulation step $`\Delta{t}`$ (time resolution) |

## References

[NESTML]: #NESTML
<a name="NESTML"></a>
* [Linssen CAP, Babu PN, He J, Eppler JM, Rumpe B, Morrison A (2022). NESTML 5.1.0. Zenodo](doi:10.5281/zenodo.7071624).

[Morrison et al. (2007)]: #Morrison07_1437
<a name="Morrison07_1437"></a>
* [Morrison et al. (2007). Spike-timing dependent plasticity in balanced random networks. Neural Computation 19:1437-1467](10.1162/neco.2007.19.6.1437)

[Rotter & Diesmann (1999)]: #Rotter99_381
<a name="Rotter99_381"></a>
* [Rotter & Diesmann (1999). Exact digital simulation of time-invariant linear systems with applications to neuronal modeling. Biological Cybernetics 81(5-6):381-402. doi:10.1007/s004220050570](https://doi.org/10.1007/s004220050570)

[NEST]: #NEST
<a name="NEST"></a>
* [Spreizer et al. (2022). NEST 3.3. Zenodo. doi:10.5281/zenodo.6368024](https://doi.org/10.5281/zenodo.6368024)
