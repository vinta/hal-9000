---
description: Toggle HAL 9000 voice clips on or off
allowed-tools:
  - Bash(python3 *)
---

Toggle the hal-voice plugin on or off by flipping `enabled` in config.json.

Run this command:

```bash
python3 -c "
import json
from pathlib import Path

config_path = Path('${CLAUDE_PLUGIN_ROOT}') / 'config.json'
defaults = {'enabled': True, 'volume': 0.5, 'debounce_seconds': 5, 'replay_suppression_seconds': 3, 'suppress_subagent_complete': True}

try:
    config = defaults | json.loads(config_path.read_text())
except (FileNotFoundError, json.JSONDecodeError):
    config = dict(defaults)

config['enabled'] = not config['enabled']
config_path.write_text(json.dumps(config, indent=2))
state = 'enabled' if config['enabled'] else 'disabled'
print(f'hal-voice: sounds {state}')
"
```

Print the output to the user exactly as returned.
