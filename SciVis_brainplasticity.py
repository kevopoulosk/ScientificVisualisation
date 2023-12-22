

import numpy as np
import pandas as pd 
import matplotlib.pyplot as plt



def PlasticityChanges(sim):
    """
    Function that visualises the lineplots for the deletion and creation of synapses for all simulations
    """
    # load the data
    data_plasticity = f"/Files/rank_0_plasticity_changes_{sim}.txt"

    # preprocess the data
    df = pd.read_csv(data_plasticity, delimiter=' ')
    df['#step:'] = df['#step:'].str.replace(':', '').astype(int)

# visulalise the creations - deletions - netto
    fig, axs = plt.subplots(3,1, figsize=(10,7))
    axs[0].semilogy(df["#step:"], df["creations"])
    axs[0].set_title(f'Creation of synapses for simulation {sim}')
    axs[0].set_ylabel('New synapses created')
    axs[0].set_xlabel("Timesteps (t)")

    axs[1].semilogy(df["#step:"], df["deletions"])
    axs[1].set_title(f'Deletion of synapses for simulation {sim}')
    axs[1].set_ylabel('Deleted synapses')
    axs[1].set_xlabel("Timesteps (t)")

    axs[2].semilogy(df["#step:"], df["netto"])
    axs[2].set_title(f'Net Amount of synapses for simulation {sim}')
    axs[2].set_ylabel('Net amount')
    axs[2].set_xlabel("Timesteps (t)")
    plt.tight_layout()
    




# For 5 timesteps of the simulations (equally spaced in time), plot the brain connectivity. 
Sims = ['calcium', 'disable', 'stimulus', 'nonetwork']
for sim in Sims:
    PlasticityChanges(sim)
    


