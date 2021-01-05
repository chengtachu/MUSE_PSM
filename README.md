
## MUSE_PSM

---

MUSE_PSM is the power sector module in The ModUlar energy system Simulation Environment (MUSE) which is modelling framework developed at Imperial College London for assessing long-term decarbonization pathways of regional or global energy systems. This framework is featured with its wide sectoral scope and agent-based structure. MUSE-Global is an implementation of a global model in this framework. The latest global simulation results can be accessed from [this web interface](http://www.museenergysimulator.co.uk/). More details about this framework is available [here](http://paris-reinforce.epu.ntua.gr/detailed_model_doc/muse).


### Power Sector Module in the MUSE framework
Within the MUSE framework, the power sector module is designed to simulate capacity investment and dispatch decisions for each regions in the model. This module receives carbon price, fuel price and power demand projections as input from the core algorithm in MUSE, as well as commodity definitions and temporal and spatial settings. Other exogenous inputs include techno-economic assumptions of each technology, regional renewable potential and generation profile, and existing power plants in every region. The module generates power price and consumption of each type of fuel, then feeds back the output to the MUSE core algorithm. Other key outputs include capacity changes of every technology, generation mix, emission, and the breakdown of total system investment.

The module is designed to accommodate a configurable investment algorithm depending on the characteristics of each regional market. Two market types of models have been implemented in the module – “**Vertically-integrated**” and “**Wholesale Market**” models. Since the module is required to finish a single iteration in MUSE within one minute, the two models are based on simulation approach. The simulation considers the constraints on regional renewable potential, a reliability requirement, and the market investment criteria to reflect real world decision making. In the Vertically-integrated model, the investment decision and dispatch operation are based on minimising total system cost and are using levelised energy cost for ranking the priority. Conversely, the Wholesale Market model is designed to simulate power sector development in the countries with established power markets. In this model, dispatch decisions are based on the least marginal generation cost (merit order). For new investments, a constraint on positive net present value (NPV) is applied to guarantee profitability. Both models considers vintage plants and decommission.

### This independent power sector simulation package
The power module in the MUSE framework has been modified into an independent package freely accessible in this repository. All model settings and assumptions are imported through excel or csv files, and model outputs will be csv files in corresponding folders. This package offers greater flexibility in several aspects than the MUSE framework.

### Main features
* Simulation based model
* Taking into account both long-term investment decisions and short-term power dispatch
* Integrating variable renewable energy generation into a system
* Satisfying system reliability requirement with increasing share of VRE

### Extensions from the Power Sector Module 
* Flexibility on configuring market structure, timeslices, simulation horizon, foresight periods and technologies
* Sub-regional simulation with trading 
* Electricity pool and power exchange market simulation
* **Power flow simulation**
* Multiple **VRE generation tranche** integration
* **Unit commitment simulation**
* **Ancillary service requirement** and dispatch simulation
* (Agent-based modelling framework)

Note that this package is an extensions from the MUSE Power Sector Module. **The agent-based mechanism and wholesale market model are still unfinished for the time being.**

---
### Methodology:
#### Dispatch simulation
* Power dispatch based on merit-order stack of all generation unit in a region
* VRE output treated as must-run with given capacity factor in each timeslice; hydropower generation based on demand profile; hydro pumped units operate based on residual demand shape
* Thermal generation unit split into must-run and dispatchable blocks
#### Future investment simulation
* Simulating power dispatch with each candidate technology in future time steps
* Considering unit decommission and capacity installation limit
* Ranking the NPV of all available candidate for each round of new investment, and install the best one
* Simulation stops until reliability requirement has been satisfied for all timeslice

---
### Major Technologies:
**Conventional Thermal Generation :**
* Coal Subcritical / Supercritical / Ultra-supercritical / IGCC
* Coal USC post comb capture CCS / oxy-fuelling CCS / IGCC pre-comb capture CCS
* Gas gas turbine / Combined-cycle
* Gas NGCC post com / oxy-fuelling capture CCS
* Oil Steam turbine
* Nuclear LWR

**Renewable and Others:**
* Biomass Steam cycle / BIGCC with CCS
* Geothermal
* Hydro large/small hydro
* Wind onshore/offshore
* Solar PV rooftop/utility scale 
* CSP
* Hydro Pump Storage

Note: the listed technologies are further spited according to fuel type  

---
### Model and Simulation Structure

Modelling different market structures: 
* one country has several market (US)
* several country participate in one market (EU)
* vertical-integrated system

Structure design:
* A country may have several zones which are the basic nodes in the model.
* Each zone participate in one market.
* A country may have zones in different market
* Each market may have several agents (GenCo) while in VI model there is only one agent
* Parameters and assumptions mainly apply on country or region level
* Simulation result will be output on zonal basis, then being aggregated into country, then into region
* All inputs in the same market will adjust to the same time zone 

![Structure](/img/simulation_structure.png)

---
### Roles and functions in the agent-based models :

### Vertically-integrated (VI) model
**Regulator(RG):**
* Capacity adequacy
* Ancillary service requirement
* Carbon price, fuel tax, renewable support

**Vertical-integrated operator(OPR):** 
* Capacity planning (LCOE priority)
* Daily unit commitment with operation reserve
* Daily storage operation
* OPF dispatch operation
* Transmission upgrade
* CHP operation

##### the main algorithm of the VI model
![VI](/img/VI_Alg.png)

### Wholesale Market (WM) model
**Regulator(RG):**
* Capacity adequacy
* Ancillary service requirement
* Carbon price, fuel tax, renewable support

**Generation Companies(GenCo):**
* Capacity investment
* DA offers with adaptive learning
* Scheduling
* CHP operation
* Capacity market offer and ancillary service

**Market/System operator(MO/SO):** 
* Day-ahead market
* Unit commitment with co-optimized operation reserve
* Security constrained economic dispatch
* Annual capacity market
* Transmission upgrade

##### the main algorithm of the WM model
![WM](/img/WM_Alg.png)

---

### Algorithms of the key functions

#### A4. Unit commitment
![UC](/img/A4_UC.png)

#### A5. Power dispatch with transmission constraints

**Power dispatch algorithm**
![A5](/img/A5_01.png)

**Cross-zone transmission algorithm**
![A5](/img/A5_02.png)

**Cross-zone transmission algorithm – example**
![A5](/img/A5_03.png)

#### A8. Heat and CHP investment algorithm
![A8](/img/A8_CHP.png)

#### A9. Capacity expansion investment algorithm
![A9](/img/A9_CE.png)


---
### License
This package is licensed under the [MIT License](/LICENSE).

