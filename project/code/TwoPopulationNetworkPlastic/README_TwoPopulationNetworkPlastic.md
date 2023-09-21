# TwoPopulationNetworkPlastic

## Overview

The ```TwoPopulationNetworkPlastic``` model describes the dynamics of a local cortical circuit at the spatial scale of ~1mm within a single cortical layer. It is derived from the model proposed in (Brunel, 2000), but accounts for the synaptic weight dynamics for connections between excitatory neurons. The weight dynamics are described by the spike-timing-dependent plasticity (STDP) model derived by Morrison et al. (2007). The model provides a mechanism underlying the formation of broad distributions of synaptic weights in combination with asynchronous irregular spiking activity (see figure below).

| **Spiking activity** | **Synaptic weight distributions** |
|--|--|
| <img src="PyNEST/figures/iaf_psc_alpha_nest/TwoPopulationNetworkPlastic_spikes.png" width="400"/> | <img src="PyNEST/figures/iaf_psc_alpha_nest/TwoPopulationNetworkPlastic_weight_distributions.png" width="400"/> |

*Spiking activity (left) and distributions of excitatory synaptic weights (right) before ("pre sim.") and after 10s simulation ("post sim.").*

| **Connectivity matrix (pre sim)** | **Connectivity matrix (post sim)** |
|--|--|
| <img src="PyNEST/figures/iaf_psc_alpha_nest/TwoPopulationNetworkPlastic_connectivity_presim.png" width="400"/> | <img src="PyNEST/figures/iaf_psc_alpha_nest/TwoPopulationNetworkPlastic_connectivity_postsim.png" width="400"/> |

*Connectivity matrices for a subset of 100 excitatory neurons before (left) and after 10s simulation (right).*

A variant of this model, the [```hpc_benchmark```](https://github.com/nest/nest-simulator/blob/master/pynest/examples/hpc_benchmark.py) has been used in a number of benchmarking studies, in particular for weak-scaling experiments (Helias et al., 2012; Kunkel et al., 2012; Ippen et al., 2017; Kunkel & Schenk, 2017; Jordan et al., 2018). Due to its random homogeneous connectivity, the model represents a hard benchmarking scenario: each neuron projects with equal probability to any other neuron in the network. Implementations of this model can therefore not exploit any spatial connectivity patterns. In contrast to the ```TwoPopulationNetworkPlastic``` testcase provided here, the plasticity dynamics in the ```hpc_benchmark``` is parameterized such that it has only a weak effect on the synaptic weights and, hence, the network dynamics. In the ```TwoPopulationNetworkPlastic``` testcase, the effect of the synaptic plasticity is substantial and leads to a significant broadening of the weight distribution (see figure above). Synaptic weights thereby become a sensitive target metric for verification and validation studies.

## Scalability

The ```TwoPopulationNetworkPlastic``` testcase can be configured into a truly scalable mode by replacing the integrate-and-fire neurons by an [```ignore_and_fire```](nestml_models/doc/ignore_and_fire.md) dynamics (for details, see [PyNEST implementation](PyNEST/README_TwoPopulationNetworkPlastic_PyNEST.md)). By doing so, the spike generation dynamics is decoupled from the input integration and the plasticity dynamics; the overall network activity, and, hence, the communication load, is fully controlled by the user. The plasticity dynamics remains intact (see figure below). 

|                      | `iaf_psc_alpha_nest`                                                                                            | `iaf_psc_alpha_nestml`                                                                                            | `ignore_and_fire_nestml`                                                                                            |
| --                   | --                                                                                                              | --                                                                                                                | --                                                                                                                  |
| spiking activity     | <img src="PyNEST/figures/iaf_psc_alpha_nest/TwoPopulationNetworkPlastic_spikes.png" width="400"/>               | <img src="PyNEST/figures/iaf_psc_alpha_nestml/TwoPopulationNetworkPlastic_spikes.png" width="400"/>               | <img src="PyNEST/figures/ignore_and_fire_nestml/TwoPopulationNetworkPlastic_spikes.png" width="400"/>               |
| weight distributions | <img src="PyNEST/figures/iaf_psc_alpha_nest/TwoPopulationNetworkPlastic_weight_distributions.png" width="400"/> | <img src="PyNEST/figures/iaf_psc_alpha_nestml/TwoPopulationNetworkPlastic_weight_distributions.png" width="400"/> | <img src="PyNEST/figures/ignore_and_fire_nestml/TwoPopulationNetworkPlastic_weight_distributions.png" width="400"/> |

*Spiking activity (top) and synaptic weight distributions (bottom) of the ```TwoPopulationNetworkPlastic``` testcase with  integrate-and-fire neuron and plasticity dynamics implemented in [NEST](https://www.nest-simulator.org) (```iaf_psc_alpha_nest```), with the same dynamics specified with [NESTML](https://github.com/nest/nestml) (```iaf_psc_alpha_nestml```), and with  [```ignore_and_fire```](nestml_models/doc/ignore_and_fire.md) and plasticity dynamics implemented in NESTML (```ignore_and_fire_nestml```).*

The `ignore_and_fire` variant of the model permits exact scaling experiments, without the need for any parameter tuning when changing the network size (see figure below). 

|                                                     |
|-----------------------------------------------------|
| <img src="PyNEST/scaling/scaling.png" width="400"/> |

*Dependence of the simulation time (top), the time and population averaged firing rate (middle) and the synaptic weights (bottom) on the network size $`N`$ for different flavors of the  ```TwoPopulationNetworkPlastic``` testcase. The in-degree $`K=1250`$ is fixed. Figure generated by [this script](PyNEST/scaling/scaling.py).*

## [Model description](doc/ModelDescription_TwoPopulationNetworkPlastic.pdf)

## [Model characteristics](PyNEST/reference_data/iaf_psc_alpha_nest/model_characteristics.json)

## Available implementations
* PyNEST ([README](PyNEST/README_TwoPopulationNetworkPlastic_PyNEST.md), [code](PyNEST/model.py))

## Model validation metrics

* distribution of time averaged single-neuron firing rates
* distribution of population firing rate
* inter-spike interval distribution 
* distribution of spike-count correlation coefficients
* distributions of synaptic weights

## References

[Brunel (2000). Dynamics of networks of randomly connected excitatory and inhibitory spiking neurons. Journal of Physiology-Paris 94(5-6):445-463. doi:10.1023/A:1008925309027](https://doi.org/10.1023/A:1008925309027)

[Helias M, Kunkel S, Masumoto G, Igarashi J, Eppler JM, Ishii S, Fukai T, Morrison A, Diesmann M (2012).  Supercomputers ready for use as discovery machines for neuroscience.  Frontiers in Neuroinformatics 6:26](https://doi.org/10.3389/fninf.2012.00026)

[Ippen T, Eppler JM, Plesser HE, Diesmann M (2017). Constructing neuronal network models in massively parallel environments.  Frontiers in Neuroinformatics 11:30](https://doi.org/10.3389/fninf.2017.00030)

[Jordan J, Ippen T, Helias M, Kitayama I, Sato M, Igarashi J, Diesmann M, Kunkel S (2018). Extremely scalable spiking neuronal network simulation code: from laptops to exascale computers.  Frontiers in Neuroinformatics 12:2](https://doi.org/10.3389/fninf.2018.00002)

[Kunkel S, Potjans TC, Eppler JM, Plesser HE, Morrison A, Diesmann M (2012). Meeting the memory challenges of brain-scale simulation. Frontiers in Neuroinformatics 5:35](https://doi.org/10.3389/fninf.2011.00035)

[Kunkel S, Schenck W (2017). The NEST dry-run mode: Efficient dynamic analysis of neuronal network simulation code. Frontiers in Neuroinformatics 11:40](https://doi.org/10.3389/fninf.2017.00040)

[Linssen CAP, Babu PN, He J, Eppler JM, Rumpe B, Morrison A (2022). NESTML 5.1.0. Zenodo](doi:10.5281/zenodo.7071624).

[Morrison A, Aertsen A, Diesmann M (2007). Spike-timing-dependent plasticity in balanced random networks. Neural Computation 19(6):1437-1467](https://doi.org/10.1162/neco.2007.19.6.1437)

