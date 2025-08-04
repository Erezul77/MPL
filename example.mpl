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
