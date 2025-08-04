# Monad Programming Language (MPL)

### A minimalist, programmable simulation framework for voxel-based causal agents

---

## 📜 What is MPL?

**MPL** (Monad Programming Language) is a conceptual and programmable system for defining *monads* — simulated entities that:

* Possess internal **state** and **memory**
* React to local **fields** and **tick-based triggers**
* Can **mutate their own rules** based on causal interactions

It’s designed to model **programmable voxel-based worlds**, inspired by Leibniz’s *monadology*, Spinoza’s metaphysics, and modern field-based simulations.

---

## 🧪 Features

* Monad definitions using `.mpl` syntax (state, memory, rules, meta-rules)
* Field-based conditions (`on field(...) { ... }`)
* Event triggers (`on tick(t) { ... }`)
* Meta-rule blocks for evolving logic
* Adequacy scoring (clarity, simplicity, success)
* Causal trace logging and export
* Visual simulation grid with click-inspection

---

## 🗂 Project Structure

* `interpreter.py` – Core execution engine for monads
* `visualizer.py` – Optional grid rendering tool (matplotlib)
* `example.mpl` – Sample monad definition
* `snapshot.json` – Output: final monad state, rules, trace
* `trace.json` – Output: causal history log

---

## 🚀 How to Use

### 1. Create a `.mpl` script:

```mpl
monad GlowCell {
  state: 'solid';
  memory: {heat_count: 0};

  on field(temperature > 60) {
    memory.heat_count += 1;
    if (memory.heat_count > 2) {
      state => 'liquid';
    }
  }

  rule-modifier {
    if state == 'liquid' {
      add_rule(on field(light > 0.8) { state => 'glow'; });
    }
  }
}
```

### 2. Run the interpreter:

```bash
python interpreter.py example.mpl
```

Outputs:

* Tick-by-tick simulation states
* Adequacy score
* `snapshot.json`, `trace.json`

### 3. Visualize (optional):

```python
from visualizer import run_simulation
run_simulation(sim, steps=10)
```

---

## 🔍 Debugging & Introspection

* Click on grid cells to inspect `state`, `memory`, and `trace_log`
* Use `monad.adequacy_score()` to measure behavior quality
* Export snapshots for reproducibility or training

---

## 🔧 For Developers

* Extend `interpreter.py` with new rule types, reward functions
* Add field types or physics logic
* Build live GUI / web canvas integrations

---

## 🌱 Roadmap

* 3D voxel support
* Neighbor interaction grammar
* Ontological debugger (real-time rule tree viewer)
* Inter-agent messaging
* Probabilistic field influence

---

## 👤 Authors

**Monad Research Project** – Integrating metaphysics, simulation, and programmable intelligence.

Learn more at: [noesis-net.org](https://noesis-net.org) (upcoming)

---

## 📄 License

MIT License — free to use, extend, remix.
