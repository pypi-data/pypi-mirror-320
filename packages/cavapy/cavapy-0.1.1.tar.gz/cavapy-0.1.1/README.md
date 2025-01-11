# Introduction
cavapy is a Python library that allows retrieval of climate data hosted in THREDDS servers at the University of Cantabria thanks to the [CAVA project](https://risk-team.github.io/CAVAanalytics/articles/CAVA.html). 

## Data source
The climate data is available at the THREDDS data server of the University of Cantabria as part of the CAVA (Climate and Agriculture Risk Visualization and Assessment) product developed by FAO, the University of Cantabria, the University of Cape Town and Predictia. 
CAVA has available CORDEX-CORE climate models, the high resolution (25 Km) dynamically-downscaled climate models used in the IPCC report AR5. Additionally, CAVA  offers access to state-of-the-art reanalyses datasets, such as ERA5 and the observational dataset W5E5 v2.

The currently available data is:

- CORDEX-CORE simulations (3 GCMs donwscaled with 2 RCMs for two RCPs)
- W5E5 and ERA5 datasets
  
Available variables:

- Daily maximum temperature (tasmax) (°C)
- Daily minimum temperature (tasmin) (°C)
- Daily precipitation (pr) (mm)
- Daily relative humidity (hurs) (%)
- Daily wind speed (sfcWind) (2 m level m/s)
- Daily solar radiation (rsds) (W/m^2)


## Installation
cavapy can be installed with pip. Ensure that you are not using a python version > 13. 

```
conda create -n test python=3.11
conda activate test
pip install cavapy
```
## Process

The get_climate_data function performs automatically:
- Data retrieval in parallel
- Unit conversion
- Convert into a Gregorian calendar (CORDEX-CORE models do not have a full 365 days calendar) through linear interpolation
- Bias correction using the empirical quantile mapping (optional)

## Example usage

Depending on the interest, downloading climate data can be done in a few different ways. Note that GCM stands for General Circulation Model while RCP stands for Regional Climate Model. As the climate data comes from the CORDEX-CORE initiative, users can choose between 3 different GCMs downscaled with two RCMs. In total, there are six simulations for any given domain (except for CAS-22 where only three are available).
Since bias-correction requires both the historical run of the CORDEX model and the observational dataset (in this case ERA5), even when the historical argument is set to False, the historical run will be used for learning the bias correction factor.

It takes about 10 minutes to run each of the tasks below. For bigger areas/country, the computational time increases. For example, for Zambia it takes about 30 minutes.

### Bias-corrected climate projections
```
import cavapy
Togo_climate_data = cavapy.get_climate_data(country="Togo", cordex_domain="AFR-22", rcp="rcp26", gcm="MPI", rcm="REMO", years_up_to=2030, obs=False, bias_correction=True, historical=False)
```
### Non bias-corrected climate projections

```
import cavapy
Togo_climate_data = cavapy.get_climate_data(country="Togo", cordex_domain="AFR-22", rcp="rcp26", gcm="MPI", rcm="REMO", years_up_to=2030, obs=False, bias_correction=False, historical=False)
```
### Bias-corrected climate projections plus the historical run

This is useful when assessing changes in crop yield from the historical period. In this case, we provide the bias-corrected historical run of the climate models plus the bias-corrected projections. 

```
import cavapy
Togo_climate_data = cavapy.get_climate_data(country="Togo", cordex_domain="AFR-22", rcp="rcp26", gcm="MPI", rcm="REMO", years_up_to=2030, obs=False, bias_correction=True, historical=True)
```
### Observations only (ERA5)

```
import cavapy
Togo_climate_data = cavapy.get_climate_data(country="Togo", cordex_domain="AFR-22", rcp="rcp26", gcm="MPI", rcm="REMO", years_up_to=2030, obs=True, bias_correction=True, historical=True, years_obs=range(1980,2019))
```
