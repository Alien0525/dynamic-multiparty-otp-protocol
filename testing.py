"""
Enhanced Testing Program (Terminal)
Uses the Single Source of Truth protocol.py
"""
import random
import sys
from protocol import ThreePartyProtocol

def get_party_state_str(protocol, party):
    if not protocol.has_sent[party]:
        if party == protocol.middle_party:
             return f"[{protocol.n // 2}, {protocol.n // 2}]"
        return str(protocol.last_used[party])
        
    if party == protocol.middle_party:
        return f"[{protocol.middle_left_boundary[party]}, {protocol.middle_right_boundary[party]}]"
    else:
        return str(protocol.last_used[party])

def print_final_statistics(protocol, attempts, blocked):
    stats = protocol.get_stats()
    n = protocol.n
    print(f"\n{'='*90}")
    print(f"FINAL SESSION STATISTICS")
    print(f"{'='*90}")
    print(f"{'Party':<10} {'Sent':<10} {'Blocked':<10} {'Total':<15} {'Success':<15}")
    print("-" * 60)
    for p in ['A', 'B', 'C']:
        total = attempts[p]
        sent = stats['sent'][p]
        blk = blocked[p]
        rate = (sent / total * 100) if total > 0 else 0.0
        print(f"{p:<10} {sent:<10} {blk:<10} {total:<15} {rate:.1f}%")
    print("-" * 60)
    print(f"Total Pads Used: {stats['used']}/{n}")
    print(f"Wastage: {stats['wasted']} pads")
    print(f"{'='*90}\n")

def run_interactive_mode():
    n = 100
    d = 5
    protocol = ThreePartyProtocol(n, d)
    
    print(f"\nINTERACTIVE TEST MODE: n={n}, d={d}")
    print(f"Initial: {protocol.left_party}(L) - {protocol.middle_party}(M) - {protocol.right_party}(R)")
    
    step = 0
    attempts_count = {'A': 0, 'B': 0, 'C': 0}
    blocked_count = {'A': 0, 'B': 0, 'C': 0}
    
    while True:
        # Get current stats for the prompt
        stats = protocol.get_stats()
        remaining = stats['total'] - stats['used']
        current_config = f"({protocol.left_party}-{protocol.middle_party}-{protocol.right_party})"
        
        # New Info Block
        print(f"\nCurrent Config {current_config}")
        print(f"Pads Remaining: {remaining}")

        try:
            user_input = input(f"Enter counts (Left, Middle, Right) [e.g. 5,10,5] or 'q': ")
            if user_input.lower() == 'q': break
            
            schedule = []
            parts = user_input.replace(',', ' ').split()
            
            if len(parts) == 3:
                try:
                    l, m, r = map(int, parts)
                    # Add messages to schedule based on current roles
                    schedule.extend([protocol.left_party] * l)
                    schedule.extend([protocol.middle_party] * m)
                    schedule.extend([protocol.right_party] * r)
                    
                    # Randomized by default
                    random.shuffle(schedule)
                    print(f"Batch: {len(schedule)} messages (Asynchronous/Randomized)")
                    
                except ValueError:
                    print("Invalid input. Use integers.")
                    continue
            else:
                print("Please enter exactly 3 numbers.")
                continue

            batch_blocked = False

            for party in schedule:
                attempts_count[party] += 1
                
                if protocol.can_send(party):
                    pad = protocol.send_message(party)
                    if pad:
                        step += 1
                        a = get_party_state_str(protocol, 'A')
                        b = get_party_state_str(protocol, 'B')
                        c = get_party_state_str(protocol, 'C')
                        conf = f"{protocol.left_party}-{protocol.middle_party}-{protocol.right_party}"
                        print(f"{step:<6} {party:<6} {pad:<6} A:{a:<10} B:{b:<10} C:{c:<10} {conf}")
                else:
                    blocked_count[party] += 1
                    print(f"⚠ Party {party} BLOCKED")
                    batch_blocked = True
            
            if batch_blocked:
                print("\n*** DEADLOCK DETECTED - ENDING SIMULATION ***")
                break
            
        except KeyboardInterrupt:
            break
            
    print_final_statistics(protocol, attempts_count, blocked_count)

if __name__ == "__main__":
    run_interactive_mode()