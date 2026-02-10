"""
suite.py - Monte Carlo Stress Testing for Dynamic 3-Party OTP
"""
import random
import time
import statistics
from protocol import ThreePartyProtocol

# --- Configuration ---
# Test different scales (N) and delay parameters (d)
TEST_CONFIGS = [
    {'n': 50,   'd': 3},
    {'n': 100,  'd': 5},
    {'n': 200,  'd': 10},
    {'n': 500,  'd': 20},
    {'n': 1000, 'd': 50},
]

# How many simulations to run per configuration
ITERATIONS = 1000 

def run_single_simulation(n, d):
    """
    Runs a single session until deadlock or exhaustion.
    Returns: Percentage of wastage (0.0 to 100.0)
    """
    protocol = ThreePartyProtocol(n, d)
    
    # Randomize Traffic Weights for this specific run
    # This simulates scenarios where one party is faster than others
    weights = [random.random() for _ in range(3)]
    total_w = sum(weights)
    norm_weights = [w/total_w for w in weights] # [Prob_A, Prob_B, Prob_C]
    parties = ['A', 'B', 'C']

    while True:
        # 1. Select a party based on random weights (Traffic Skew)
        party = random.choices(parties, weights=norm_weights, k=1)[0]
        
        # 2. Check if this specific move is possible
        if protocol.can_send(party):
            protocol.send_message(party)
        else:
            # 3. If the selected party is blocked, we try the others to see 
            # if it's a true deadlock or just a party-specific block.
            # (In a real async network, other parties might still move).
            possible_moves = [p for p in parties if protocol.can_send(p)]
            
            if not possible_moves:
                # TRUE DEADLOCK: No one can move.
                break
            else:
                # If others can move, force one of them to proceed 
                # to maximize pad usage (greedy approach).
                alt_party = random.choice(possible_moves)
                protocol.send_message(alt_party)
                
        # Check if pad is full (Optimization to stop early)
        if len(protocol.used_pads) == n:
            break

    stats = protocol.get_stats()
    return (stats['wasted'] / n) * 100.0

def print_header():
    print(f"{'N':<8} {'d':<6} {'Sims':<8} | {'Avg Waste %':<15} {'Worst Waste %':<15} {'Best Waste %':<15}")
    print("-" * 80)

def main():
    print(f"\nRunning Monte Carlo Stress Test (Iterations={ITERATIONS})...\n")
    print_header()

    for config in TEST_CONFIGS:
        n = config['n']
        d = config['d']
        
        results = []
        
        start_time = time.time()
        
        for _ in range(ITERATIONS):
            wastage = run_single_simulation(n, d)
            results.append(wastage)
        
        elapsed = time.time() - start_time
        
        # Calculate Statistics
        avg_waste = statistics.mean(results)
        worst_waste = max(results) # Max wastage = Worst Case
        best_waste = min(results)  # Min wastage = Best Case
        
        # Print Row
        print(f"{n:<8} {d:<6} {ITERATIONS:<8} | {avg_waste:<15.2f} {worst_waste:<15.2f} {best_waste:<15.2f}")

    print("-" * 80)
    print("\nLegend:")
    print("  N: Total Pad Size")
    print("  d: Delay Parameter")
    print("  Avg Waste %: The mean space lost due to fragmentation.")
    print("  Worst Waste %: The highest fragmentation observed (early deadlock).")
    print("  Best Waste %: 0.00 means the protocol successfully used every single pad.")

if __name__ == "__main__":
    main()