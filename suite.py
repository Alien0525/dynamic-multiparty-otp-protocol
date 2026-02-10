"""
suite.py - Stratified Monte Carlo Simulation (Scenario Testing)
Covers S.1, S.2, S.3 with specific sub-cases and global aggregation.
"""
import random
import statistics
from protocol import ThreePartyProtocol

# --- Configuration ---
# Testing for d <= 10% of n
TEST_CONFIGS = [
    {'n': 10,  'd': 1},
    {'n': 50,  'd': 3},
    {'n': 50,  'd': 4},
    {'n': 50,  'd': 5},
    {'n': 100, 'd': 5}, 
    {'n': 100, 'd': 7}, 
    {'n': 100, 'd': 10},
    {'n': 200, 'd': 10},
    {'n': 200, 'd': 15},
    {'n': 200, 'd': 20},
    {'n': 500, 'd': 10},
    {'n': 500, 'd': 25},
    {'n': 500, 'd': 50},
    {'n': 1000, 'd': 10},
    {'n': 1000, 'd': 50},
    {'n': 1000, 'd': 100},
]

ITERATIONS = 1000 

def run_simulation(n, d, active_subset):
    """
    Runs a simulation where ONLY 'active_subset' parties are allowed to talk.
    Returns: % Wastage
    """
    protocol = ThreePartyProtocol(n, d)
    
    # Randomize "Personality" (Weights) for the ACTIVE subset
    weights = [random.random() for _ in active_subset]
    total_w = sum(weights)
    norm_weights = [w/total_w for w in weights]
    
    while True:
        # Pick one party from the ACTIVE list
        party = random.choices(active_subset, weights=norm_weights, k=1)[0]
        
        # Try to send
        if protocol.can_send(party):
            protocol.send_message(party)
        else:
            # If blocked, check if OTHER active parties can move
            others = [p for p in active_subset if protocol.can_send(p)]
            if not others:
                break # Deadlock among active parties
            
            # Force move from another active party
            alt = random.choice(others)
            protocol.send_message(alt)
            
        if len(protocol.used_pads) == n:
            break

    stats = protocol.get_stats()
    return (stats['wasted'] / n) * 100.0

def main():
    print(f"\n3-PARTY PROTOCOL TESTING SUITE (N={len(TEST_CONFIGS)}, Iterations={ITERATIONS}/scenario)")
    
    # Define Header Columns
    header_cols = (
        f"{'N':<5} {'d':<4} | "
        f"{'S.1 End':<9} {'S.1 Mid':<9} | "
        f"{'S.2 Ends':<9} {'S.2 Mix':<9} | "
        f"{'S.3 All':<9} | "
        f"{'Best %':<7} {'Worst %':<7} {'Avg %':<7}"
    )
    
    # Calculate ruler length based on header
    ruler = "=" * len(header_cols)
    
    print(ruler)
    print("DEFINITIONS:")
    print("  * Initial End Parties  : A (Left), B (Right)")
    print("  * Initial Middle Party : C (Center)")
    print(ruler)
    
    # Print Table Header
    print(header_cols)
    print("-" * len(header_cols))
    
    for config in TEST_CONFIGS:
        n = config['n']
        d = config['d']
        
        # Storage for results
        res_s1_end = []
        res_s1_mid = []
        res_s2_ends = []
        res_s2_mix = []
        res_s3 = []
        
        # Master list for global stats (combines all scenarios)
        all_runs_for_config = []
        
        for _ in range(ITERATIONS):
            # --- S.1 Scenarios ---
            # Case A: End Party (A or B)
            party_s1_end = random.choice([['A'], ['B']])
            val = run_simulation(n, d, party_s1_end)
            res_s1_end.append(val)
            all_runs_for_config.append(val)
            
            # Case B: Middle Party (C)
            val = run_simulation(n, d, ['C'])
            res_s1_mid.append(val)
            all_runs_for_config.append(val)
            
            # --- S.2 Scenarios ---
            # Case A: Ends only (A and B)
            val = run_simulation(n, d, ['A', 'B'])
            res_s2_ends.append(val)
            all_runs_for_config.append(val)
            
            # Case B: Mixed (Middle involved) -> (A,C) or (B,C)
            party_s2_mix = random.choice([['A', 'C'], ['B', 'C']])
            val = run_simulation(n, d, party_s2_mix)
            res_s2_mix.append(val)
            all_runs_for_config.append(val)
            
            # --- S.3 Scenario ---
            val = run_simulation(n, d, ['A', 'B', 'C'])
            res_s3.append(val)
            all_runs_for_config.append(val)
            
        # Calculate Scenario Averages
        avg_s1_end = statistics.mean(res_s1_end)
        avg_s1_mid = statistics.mean(res_s1_mid)
        avg_s2_ends = statistics.mean(res_s2_ends)
        avg_s2_mix = statistics.mean(res_s2_mix)
        avg_s3 = statistics.mean(res_s3)
        
        # Calculate Global Extremes and Average across ALL collected runs
        global_best = min(all_runs_for_config)
        global_worst = max(all_runs_for_config)
        global_avg = statistics.mean(all_runs_for_config)
        
        # Print Row
        print(
            f"{n:<5} {d:<4} | "
            f"{avg_s1_end:<9.2f} {avg_s1_mid:<9.2f} | "
            f"{avg_s2_ends:<9.2f} {avg_s2_mix:<9.2f} | "
            f"{avg_s3:<9.2f} | "
            f"{global_best:<7.2f} {global_worst:<7.2f} {global_avg:<7.2f}"
        )

    print("-" * len(header_cols))
    print("Legend:")
    print("  S.1 End  : Only A or Only B talks (C is static)")
    print("  S.1 Mid  : Only C talks")
    print("  S.2 Ends : A and B talk (C is static)")
    print("  S.2 Mix  : One End (A/B) and Middle (C) talk")
    print("  S.3 All  : All parties active")
    print("-" * len(header_cols))
    print("Global Stats:")
    print("  * Best % : The lowest wastage % found in ANY simulated scenario for this {N,d}.")
    print("  * Worst %: The highest wastage % found in ANY simulated scenario for this {N,d}.")
    print("  * Avg %  : The mean wastage across ALL 5,000 simulations combined (S.1 + S.2 + S.3).")
    print("  * Static Limit  : 66.7% (The wastage if we just split N into 3 fixed parts and only 1 talked)")

if __name__ == "__main__":
    main()