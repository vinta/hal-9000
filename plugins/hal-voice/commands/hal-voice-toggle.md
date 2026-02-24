---
description: Toggle HAL 9000 voice clips on or off
allowed-tools:
  - Bash(python3:*)
---

Toggle the hal-voice plugin on or off by flipping `enabled` in config.json.

Run this command:

```bash
python3 -c "
import json
from pathlib import Path

config_path = Path('${CLAUDE_PLUGIN_ROOT}') / 'config.json'
try:
    config = json.loads(config_path.read_text())
except (FileNotFoundError, json.JSONDecodeError):
    config = {}

config['enabled'] = not config.get('enabled', True)
config_path.write_text(json.dumps(config, indent=2))
state = 'enabled' if config['enabled'] else 'disabled'
print(f'hal-voice: sounds {state}')
"
```

Print the output to the user exactly as returned.
