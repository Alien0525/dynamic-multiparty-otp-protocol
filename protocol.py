"""
3-Party One-Time Pad Protocol
SINGLE SOURCE OF TRUTH - Contains all logic fixes.
"""

class ThreePartyProtocol:
    def __init__(self, n, d):
        self.n = n
        self.d = d
        self.parties = ['A', 'B', 'C']
        
        # Initial Positions
        # A(Left): 0 (Virtual start, 1st move is 1)
        # B(Right): n+1 (Virtual start, 1st move is n)
        # C(Middle): n//2 (Physical start)
        self.last_used = {'A': 0, 'B': n + 1, 'C': n // 2}
        
        self.middle_left_boundary = {} 
        self.middle_right_boundary = {}
        self.has_sent = {'A': False, 'B': False, 'C': False}
        
        self.left_party = 'A'
        self.middle_party = 'C'
        self.right_party = 'B'
        
        # Initialize middle party boundaries
        self.middle_left_boundary[self.middle_party] = n // 2
        self.middle_right_boundary[self.middle_party] = n // 2
        
        self.used_pads = set()
        self.messages_sent = {'A': 0, 'B': 0, 'C': 0}
        
    def get_next_position(self, party):
        current_pos = self.last_used[party]
        
        # FIX: Phantom Start
        # Do not assume 1 or N. Trust current_pos (updated during swaps).
        if not self.has_sent[party]:
            if party == self.left_party: return current_pos + 1
            elif party == self.right_party: return current_pos - 1
            # If Middle hasn't sent, it falls through to logic below
            
        if party == self.middle_party:
            middle_left = self.middle_left_boundary[party]
            middle_right = self.middle_right_boundary[party]

            # FIX: Middle Spot
            # If strictly one spot remains and it's empty, take it.
            if middle_left == middle_right and middle_left not in self.used_pads:
                return middle_left

            # Calculate Gaps
            left_pos = self.last_used[self.left_party]
            right_pos = self.last_used[self.right_party]
            
            left_gap = middle_left - left_pos - 1
            right_gap = right_pos - middle_right - 1

            # Move towards largest gap
            if left_gap > right_gap: return middle_left - 1
            elif right_gap > left_gap: return middle_right + 1
            else: return middle_right + 1
                
        elif party == self.left_party:
            return current_pos + 1
        else:
            return current_pos - 1
    
    def check_safety(self, party, position):
        if position < 1 or position > self.n: return False
        if position in self.used_pads: return False
        
        for other in self.parties:
            if other != party:
                # FIX: Passive Boundary Safety
                # Respect boundaries even if other party hasn't sent.
                if other == self.middle_party:
                    lb = self.middle_left_boundary[other]
                    rb = self.middle_right_boundary[other]
                    if abs(position - lb) <= self.d: return False
                    if abs(position - rb) <= self.d: return False
                else:
                    other_pos = self.last_used[other]
                    if abs(position - other_pos) <= self.d: return False
        return True
    
    def reposition_if_needed(self):
        # FIX: Reposition checks against un-moved parties too
        left_pos = self.last_used[self.left_party]
        right_pos = self.last_used[self.right_party]
        middle_left = self.middle_left_boundary[self.middle_party]
        middle_right = self.middle_right_boundary[self.middle_party]
            
        # FIX: Dead Zone Trigger (d + 1)
        threshold = self.d + 1
        
        # Left <-> Middle Trigger
        if abs(middle_left - left_pos) <= threshold:
            center_gap = right_pos - middle_right
            if center_gap > self.d * 2:
                new_pos = (middle_right + right_pos) // 2
                
                old_left = self.left_party
                old_middle = self.middle_party
                
                # FIX: Ghost Pad (Resume from RIGHT boundary)
                self.last_used[old_middle] = middle_right
                
                self.left_party = old_middle
                self.middle_party = old_left
                
                self.last_used[old_left] = new_pos
                self.has_sent[old_left] = True
                self.middle_left_boundary[old_left] = new_pos
                self.middle_right_boundary[old_left] = new_pos
                return True
        
        # Middle <-> Right Trigger
        if abs(right_pos - middle_right) <= threshold:
            center_gap = middle_left - left_pos
            if center_gap > self.d * 2:
                new_pos = (left_pos + middle_left) // 2
                
                old_right = self.right_party
                old_middle = self.middle_party
                
                # FIX: Ghost Pad (Resume from LEFT boundary)
                self.last_used[old_middle] = middle_left
                
                self.right_party = old_middle
                self.middle_party = old_right
                
                self.last_used[old_right] = new_pos
                self.has_sent[old_right] = True
                self.middle_left_boundary[old_right] = new_pos
                self.middle_right_boundary[old_right] = new_pos
                return True
        
        return False
    
    def can_send(self, party):
        next_pos = self.get_next_position(party)
        return self.check_safety(party, next_pos)
    
    def send_message(self, party):
        if not self.can_send(party): return None
        
        next_pos = self.get_next_position(party)
        
        self.last_used[party] = next_pos
        self.has_sent[party] = True
        self.used_pads.add(next_pos)
        self.messages_sent[party] += 1
        
        if party == self.middle_party:
            if next_pos < self.middle_left_boundary[party]:
                self.middle_left_boundary[party] = next_pos
            if next_pos > self.middle_right_boundary[party]:
                self.middle_right_boundary[party] = next_pos
        
        self.reposition_if_needed()
        return next_pos

    def get_stats(self):
        return {
            'total': self.n,
            'used': len(self.used_pads),
            'wasted': self.n - len(self.used_pads),
            'efficiency': ((self.n - len(self.used_pads))/self.n)*100 if self.n else 0,
            'sent': self.messages_sent
        }