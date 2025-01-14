import numpy as np
import numba 
import pandas as pd 
from typing import List, Dict
from . import utils

def preprocess_participant_data(
    data_we_have: pd.DataFrame, current_order_dict: Dict
    ) -> Dict[int, Tuple[np.ndarray, np.ndarray, np.ndarray]]:
    """
    Preprocess participant data into NumPy arrays for efficient computation.

    Args:
        data_we_have (pd.DataFrame): Raw participant data.
        current_order_dict (Dict): Mapping of biomarkers to stages.

    Returns:
        Dict[int, Tuple[np.ndarray, np.ndarray, np.ndarray]]: A dictionary where keys are participant IDs,
            and values are tuples of (measurements, S_n, biomarkers).
    """
    data = data_we_have.copy()
    data['S_n'] = data['biomarker'].map(current_order_dict)

    participant_data = {}
    for participant, pdata in data.groupby('participant'):
        measurements = pdata['measurement'].values 
        S_n = pdata['S_n'].values 
        biomarkers = pdata['biomarker'].values  
        participant_data[participant] = (measurements, S_n, biomarkers)
    return participant_data

def calculate_all_participant_ln_likelihood(
    participant_data: Dict[int, Tuple[np.ndarray, np.ndarray, np.ndarray]],
    non_diseased_ids: np.ndarray,
    theta_phi: Dict[str, Dict[str, float]],
    diseased_stages: np.ndarray
    ) -> float:
    """Calculate the total log likelihood across all participants."""
    total_ln_likelihood = 0.0 
    for participant, (measurements, S_n, biomarkers) in participant_data.items():
        if participant in non_diseased_ids:
            likelihood = utils.compute_likelihood(
                measurements, S_n, biomarkers, k_j = 0, theta_phi = theta_phi
            )
        else:
            stage_likelihoods = [
                utils.compute_likelihood(
                    measurements, S_n, biomarkers, k_j = k_j, theta_phi=theta_phi
                ) for k_j in diseased_stages
            ]
            likelihood = np.mean(stage_likelihoods)
        total_ln_likelihood += np.log(likelihood + 1e-10)
    return total_ln_likelihood


def metropolis_hastings_hard_kmeans(
    data_we_have: pd.DataFrame,
    iterations: int, 
    n_shuffle: int
    ) -> List[Dict]:
    """Metropolis-Hastings clustering algorithm."""
    n_participants = len(data_we_have.participant.unique())
    biomarkers = data_we_have.biomarker.unique()
    n_stages = len(biomarkers) + 1

    non_diseased_ids = data_we_have.loc[data_we_have.diseased == False].participant.unique()
    diseased_stages = np.arange(1, n_stages)
    theta_phi_estimates = utils.get_theta_phi_estimates(data_we_have)

    current_order = np.random.permutation(np.arange(1, n_stages))
    current_order_dict = dict(zip(biomarkers, current_order))
    current_ln_likelihood = -np.inf
    acceptance_count = 0
    # Note that this records only the current accepted orders in each iteration
    all_orders = []

    for iteration in range(iterations):
        # Suffle the order 

        # Note that copy here is necessary because without it, each iteration is 
        # shuffling the order in the last iteration. 

        # With copy, we can ensure that the current state remains unchanged until
        # the proposed state is accepted.  
        new_order = current_order.copy()
        utils.shuffle_order(new_order, n_shuffle)
        new_order_dict = dict(zip(biomarkers, new_order))

        # Preprocess participant data 
        participant_data = preprocess_participant_data(data_we_have, new_order_dict)

        # Calculate likelihoods
        ln_likelihood = calculate_all_participant_ln_likelihood(
            participant_data, non_diseased_ids, theta_phi_estimates, diseased_stages
        )

        # Log-Sum-Exp trick for numerical stability 
        max_likelihood = max(ln_likelihood, current_ln_likelihood)
        prob_accept = np.exp(
            (ln_likelihood - max_likelihood) - (current_ln_likelihood - max_likelihood)
        )

        # prob_of_accepting_new_order = np.exp(
        #     all_participant_ln_likelihood - current_accepted_likelihood)

        # np.exp(a)/np.exp(b) = np.exp(a - b)
        # if a > b, then np.exp(a - b) > 1

        # Accept or reject 
        # it will definitly update at the first iteration
        if np.random.rand() < prob_accept:
            current_order = new_order 
            current_ln_likelihood = ln_likelihood
            current_order_dict = new_order_dict 
            acceptance_count += 1
        
        all_orders.append(current_order_dict)

        # Print progress every 100 iterations 
        if (iteration + 1) % max(10, iterations // 10) == 0:
            acceptance_ratio = 100 * acceptance_count / (iteration + 1)
            print(
                f"Iteration {iteration + 1}/{iterations}, "
                f"Acceptance Ratio: {acceptance_ratio:.2f}%, "
                f"Log Likelihood: {current_ln_likelihood:.4f}, "
                f"Current Accepted Order: {current_order_dict.values()} "
            )
    return all_orders
