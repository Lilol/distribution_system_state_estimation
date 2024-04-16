# Distribution System State Estimation
This repository contains Python scripts for low voltage distribution system state estimation. The codes cover all modeling steps, such as reading the network parameter files, building the network models from these files, and calling the weighted least squares method for various scenarios, validating the WLS using power-flow equations, evaluating the error metrics, and creating the comparisons.

# Required Python distribution
Before running the scripts, please install a Python distribution with version 3.9 or higher.

# Required packages
The required packages are listed in the requirement.txt file. To install all requirements, please run the following command:
> pip install -r requirements.txt

# Configuration
To set the parameters of the script, edit the configuration file in config\config.ini and the scenario specification in config\scenarios.txt

# Scripts
## Running the state estimation
This command will run the state estimation process, as well as the validation power-flow process for the time steps specified in the configuration file.
Outputs are generated in the folder specified in the [paths] output_path= option of the config file.

> python main.py

## Running the post-evaluation
This command will run the evaluation and configuration process and compute the specified performance indices.
Outputs are generated in the folder specified in the [paths] output_paths= option of the config file.

> python evaluation\main.py
