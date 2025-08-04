import re
import ast
import json

class Field:
    def __init__(self):
        self.values = {}

    def set_value(self, x, y, name, value):
        if (x, y) not in self.values:
            self.values[(x, y)] = {}
        self.values[(x, y)][name] = value

    def get_context(self, x, y):
        return self.values.get((x, y), {})


class MonadDefinition:
    def __init__(self, name, state, memory, rules, meta_rules):
        self.name = name
        self.state = state
        self.memory = memory
        self.rules = rules
        self.meta_rules = meta_rules


class Monad:
    def __init__(self, definition: MonadDefinition):
        self.name = definition.name
        self.state = definition.state
        self.memory = definition.memory.copy()
        self.rules = definition.rules[:]
        self.meta_rules = definition.meta_rules[:]
        self.rule_history = []
        self.last_triggered = []
        self.trace_log = []
        self.rule_mutations = []

    def evaluate_rules(self, rule_type, context):
        for rule in self.rules:
            if rule["type"] == rule_type:
                condition = rule.get("condition") or rule.get("trigger") or "True"
                try:
                    if eval(condition, {}, context):
                        prev_state = self.state
                        # Clean up the action code by removing all indentation
                        action_code = rule["action"].strip()
                        # Remove all leading whitespace from each line
                        lines = action_code.split('\n')
                        cleaned_lines = []
                        for line in lines:
                            cleaned_lines.append(line.lstrip())
                        action_code = '\n'.join(cleaned_lines)
                        
                        # Convert MPL syntax to Python
                        action_code = action_code.replace("=>", "=")
                        # Convert state assignments to function calls
                        action_code = action_code.replace("state = ", "state(")

                        # Convert if statement syntax
                        action_code = action_code.replace("if (", "if ")
                        action_code = action_code.replace(") {", ":")
                        # Add closing parenthesis for state assignments and fix indentation
                        lines = action_code.split('\n')
                        new_lines = []
                        for i, line in enumerate(lines):
                            if 'state(' in line and not line.strip().endswith(')'):
                                line = line.rstrip(';') + ");"
                            # Fix indentation for if blocks
                            if i > 0 and lines[i-1].strip().startswith('if ') and line.strip():
                                line = '    ' + line
                            new_lines.append(line)
                        action_code = '\n'.join(new_lines)
                        

                        # Create a memory proxy that allows dot notation
                        class MemoryProxy:
                            def __init__(self, memory_dict):
                                self._memory = memory_dict
                            
                            def __getattr__(self, name):
                                return self._memory.get(name)
                            
                            def __setattr__(self, name, value):
                                if name == '_memory':
                                    super().__setattr__(name, value)
                                else:
                                    self._memory[name] = value
                        
                        exec(action_code, {}, {
                            "state": self.state_proxy(),
                            "memory": MemoryProxy(self.memory),
                            **context
                        })
                        if self.state != prev_state:
                            self.trace_log.append({
                                "tick": context.get("t", -1),
                                "rule_type": rule_type,
                                "condition": condition,
                                "prev_state": prev_state,
                                "new_state": self.state
                            })
                        self.last_triggered.append((rule_type, condition))
                except Exception as e:
                    print(f"Error in rule ({rule_type}): {e}")

    def evaluate_field(self, field_context):
        self.evaluate_rules("field", field_context)

    def evaluate_tick(self, tick_value=None):
        context = {"t": tick_value}
        self.evaluate_rules("tick", context)

    def apply_meta_rules(self):
        for meta in self.meta_rules:
            try:
                exec(meta, {}, {"state": self.state_proxy(), "memory": self.memory, "add_rule": self.add_rule})
            except Exception as e:
                print(f"Error evaluating meta-rule: {e}")

    def state_proxy(self):
        proxy = {"__value": self.state}
        def setter(new_val):
            proxy["__value"] = new_val
            self.state = new_val
        return setter

    def add_rule(self, rule_block):
        if "on field" in rule_block:
            match = re.search(r"on field\(([^)]+)\) \{([^}]*)\}", rule_block)
            if match:
                condition, action = match.group(1), match.group(2)
                self.rules.append({"type": "field", "condition": condition.strip(), "action": action.strip()})
                self.rule_history.append(rule_block)
                self.rule_mutations.append({"tick": -1, "type": "field", "source": "meta", "rule": rule_block})
        elif "on tick" in rule_block:
            match = re.search(r"on tick\(([^)]*)\) \{([^}]*)\}", rule_block)
            if match:
                trigger, action = match.group(1), match.group(2)
                self.rules.append({"type": "tick", "trigger": trigger.strip(), "action": action.strip()})
                self.rule_history.append(rule_block)
                self.rule_mutations.append({"tick": -1, "type": "tick", "source": "meta", "rule": rule_block})

    def adequacy_score(self):
        score = 0.0
        if self.state in ['goal', 'glow']:
            score += 0.4
        trace_len = len(self.trace_log)
        score += max(0, 0.3 - 0.01 * trace_len)
        rule_count = len(self.rules)
        score += max(0, 0.3 - 0.01 * rule_count)
        return round(min(score, 1.0), 3)

    def export_debug_snapshot(self, file_path):
        snapshot = {
            "name": self.name,
            "state": self.state,
            "memory": self.memory,
            "rules": self.rules,
            "meta_rules": self.meta_rules,
            "trace_log": self.trace_log,
            "rule_mutations": self.rule_mutations,
            "adequacy": self.adequacy_score()
        }
        with open(file_path, 'w') as f:
            json.dump(snapshot, f, indent=2)

    def export_trace_log(self, file_path):
        with open(file_path, 'w') as f:
            json.dump(self.trace_log, f, indent=2)


def parse_mpl_code(code):
    # Extract monad body with proper brace matching
    start = code.find('monad ')
    if start == -1:
        raise ValueError("Invalid monad definition")
    
    # Find the opening brace
    brace_start = code.find('{', start)
    if brace_start == -1:
        raise ValueError("Invalid monad definition")
    
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
                    break
    else:
        raise ValueError("Invalid monad definition")

    state_match = re.search(r"state:\s*'([^']+)'", body)
    state = state_match.group(1) if state_match else None

    memory_match = re.search(r"memory:\s*(\{[^}]*\})", body)
    if memory_match:
        memory_str = memory_match.group(1)
        # Convert MPL syntax to Python dict syntax
        memory_str = memory_str.replace(":", ":").replace("'", '"')
        try:
            memory = ast.literal_eval(memory_str)
        except:
            # Fallback: parse manually
            memory = {}
            pairs = memory_str.strip('{}').split(',')
            for pair in pairs:
                if ':' in pair:
                    key, value = pair.split(':', 1)
                    key = key.strip().strip('"\'')
                    value = value.strip()
                    try:
                        memory[key] = int(value)
                    except:
                        memory[key] = value
    else:
        memory = {}

    rules = []
    for match in re.finditer(r"on field\s*\(([^)]+)\)\s*\{([\s\S]*?)\}", body):
        action = match.group(2).strip()
        rules.append({"type": "field", "condition": match.group(1).strip(), "action": action})

    for match in re.finditer(r"on tick\s*\(([^)]*)\)\s*\{([\s\S]*?)\}", body):
        rules.append({"type": "tick", "trigger": match.group(1).strip(), "action": match.group(2).strip()})

    meta_rules = []
    meta_match = re.search(r"rule-modifier \{([\s\S]*?)\}$", body)
    if meta_match:
        meta_rules.append(meta_match.group(1).strip())

    return MonadDefinition(name, state, memory, rules, meta_rules)


class Simulation:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid = [[None for _ in range(width)] for _ in range(height)]
        self.field = Field()
        self.tick_count = 0

    def place_monad(self, x, y, monad):
        self.grid[y][x] = monad

    def set_field_value(self, x, y, name, value):
        self.field.set_value(x, y, name, value)

    def get_neighbors(self, x, y):
        neighbors = {}
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    neighbor = self.grid[ny][nx]
                    if neighbor:
                        neighbors[(dx, dy)] = neighbor.state
        return neighbors

    def step(self):
        for y in range(self.height):
            for x in range(self.width):
                monad = self.grid[y][x]
                if monad:
                    context = self.field.get_context(x, y)
                    context["neighbors"] = self.get_neighbors(x, y)
                    monad.evaluate_field(context)
                    monad.evaluate_tick(self.tick_count)
                    monad.apply_meta_rules()
        self.tick_count += 1

    def render_states(self):
        return [[self.grid[y][x].state if self.grid[y][x] else None for x in range(self.width)] for y in range(self.height)]


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python interpreter.py <mpl_file>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        code = f.read()

    definition = parse_mpl_code(code)

    sim = Simulation(3, 3)
    sim.place_monad(1, 1, Monad(definition))
    sim.set_field_value(1, 1, "temperature", 70)
    sim.set_field_value(1, 1, "light", 0.9)  # Add light field for the glow rule

    for i in range(4):
        print(f"\nTick {i}:")
        sim.step()
        for row in sim.render_states():
            print(row)

    monad = sim.grid[1][1]
    print("\nAdequacy:", monad.adequacy_score())
    print("\nMonad rules:", monad.rules)
    print("\nField context at (1,1):", sim.field.get_context(1, 1))
    monad.export_debug_snapshot("snapshot.json")
    monad.export_trace_log("trace.json")
