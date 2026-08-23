import json
import sys
import re

def parse_line(line: str):
    line = line.strip()
    if not line: return None, None
    
    match = re.match(r'\[(.*?)\]\s*(.*)', line)
    if not match: return None, None
    
    event_name = match.group(1)
    payload_str = match.group(2)
    payload = {}
    
    if payload_str:
        payload = json.loads(payload_str)
        
    return event_name, payload

def main():
    for line in sys.stdin:
        event_name, payload = parse_line(line)
        if event_name:
             # handle
             print(event_name)

if __name__ == '__main__':
    main()
