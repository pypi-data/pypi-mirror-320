from operationunitaire.main import run_simulation

# User Inputs
stage_temperatures = {1: 65, 2: 90, 3: 115, 4: 140, 5: 165}
feed_composition = {'C3': 0.3, 'NC4': 0.3, 'NC5': 0.4}
vapor_flow_rates = {1: 0, 2: 150, 3: 150, 4: 150, 5: 150}
feed_flow_rates = {1: 0, 2: 0, 3: 100, 4: 0, 5: 0}

# Run the simulation
run_simulation(stage_temperatures, feed_composition, vapor_flow_rates, feed_flow_rates)
