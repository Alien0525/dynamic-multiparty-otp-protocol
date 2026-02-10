"""
Simple HTTP Server to bridge the Web UI with protocol.py
Run: python server.py
Then open http://localhost:8000
"""
from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
import random
from protocol import ThreePartyProtocol

# Global state
active_protocol = None
blocked_counts = {'A': 0, 'B': 0, 'C': 0}

class ProtocolHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.path = 'index.html'
        return SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        global active_protocol, blocked_counts
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode('utf-8'))
        
        response = {}
        
        if self.path == '/init':
            n = int(data.get('n', 100))
            d = int(data.get('d', 5))
            active_protocol = ThreePartyProtocol(n, d)
            # Reset blocked counts
            blocked_counts = {'A': 0, 'B': 0, 'C': 0}
            response = {'status': 'ok', 'msg': 'Protocol Initialized'}
            
        elif self.path == '/run':
            if not active_protocol:
                self.send_error(400, "Protocol not initialized")
                return

            # Get inputs
            a_count = int(data.get('a', 0))
            b_count = int(data.get('b', 0))
            c_count = int(data.get('c', 0))
            shuffle_mode = data.get('shuffle', False)
            
            # Create batch schedule
            schedule = []
            schedule.extend(['A'] * a_count)
            schedule.extend(['B'] * b_count)
            schedule.extend(['C'] * c_count)
            
            if shuffle_mode:
                random.shuffle(schedule)
            
            trace = []
            protocol_blocked = False
            blocked_party_trigger = None
            
            for party in schedule:
                step_data = {
                    'party': party,
                    'success': False,
                    'pad': None,
                    'state': None,
                    'left_p': active_protocol.left_party,
                    'mid_p': active_protocol.middle_party,
                    'right_p': active_protocol.right_party
                }
                
                if active_protocol.can_send(party):
                    pad = active_protocol.send_message(party)
                    if pad is not None:
                        step_data['success'] = True
                        step_data['pad'] = pad
                        # Serialize state for UI
                        if party == active_protocol.middle_party:
                            step_data['state'] = [
                                active_protocol.middle_left_boundary[party],
                                active_protocol.middle_right_boundary[party]
                            ]
                        else:
                            step_data['state'] = active_protocol.last_used[party]
                    else:
                        # Logic error catch
                        protocol_blocked = True
                        blocked_party_trigger = party
                        blocked_counts[party] += 1
                else:
                    # BLOCKED!
                    protocol_blocked = True
                    blocked_party_trigger = party
                    blocked_counts[party] += 1
                
                trace.append(step_data)
                
                # NOTE: We DO NOT break here anymore. 
                # We finish the batch to count all blocked attempts.
            
            response = {
                'trace': trace,
                'stats': active_protocol.get_stats(),
                'blocked': protocol_blocked,
                'blocked_party': blocked_party_trigger,
                'blocked_counts': blocked_counts  # Send cumulative counts
            }

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode('utf-8'))

if __name__ == '__main__':
    print("Starting server on http://localhost:8000...")
    HTTPServer(('localhost', 8000), ProtocolHandler).serve_forever()