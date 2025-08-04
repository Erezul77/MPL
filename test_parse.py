import re
import sys

def extract_monad_body(code):
    """Extract monad body with proper brace matching"""
    start = code.find('monad ')
    if start == -1:
        return None, None
    
    # Find the opening brace
    brace_start = code.find('{', start)
    if brace_start == -1:
        return None, None
    
    # Find the matching closing brace
    brace_count = 0
    for i in range(brace_start, len(code)):
        if code[i] == '{':
            brace_count += 1
        elif code[i] == '}':
            brace_count -= 1
            if brace_count == 0:
                # Found the matching closing brace
                name_match = re.search(r'monad (\w+)', code[start:brace_start])
                if name_match:
                    name = name_match.group(1)
                    body = code[brace_start+1:i]
                    return name, body
    
    return None, None

# Read the example file
with open('example.mpl', 'r') as f:
    code = f.read()

print("Code:", repr(code))
sys.stdout.flush()

# Test monad extraction
name, body = extract_monad_body(code)
if name and body:
    print("Name:", name)
    print("Body:", repr(body))
    print("Body length:", len(body))
    print("Body contains 'on field':", 'on field' in body)
    
    # Test field rule extraction
    for match in re.finditer(r"on field\s*\(([^)]+)\)\s*\{([\s\S]*?)\}", body):
        print("Found field rule:", match.groups())
else:
    print("No monad match found") 