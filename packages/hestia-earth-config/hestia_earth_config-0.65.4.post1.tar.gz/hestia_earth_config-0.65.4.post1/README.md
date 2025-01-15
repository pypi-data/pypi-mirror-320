# Hestia Engine Config

> HESTIA default configuration files for the engine library.

The version of the config follows the version of the models. Example:
- to use with `hestia_earth_engine` version `0.65.0`, you can use configuration version `0.65.0.postN`, where N refers to an increment fix of the configuration.

## Usage

### JavaScript / Typescript

1. Install the library:
```bash
npm install @hestia-earth/engine-config
```
2. Import the function to load the configuration:
```typescript
import { loadConfig } from '@hestia-earth/engine-config';

const config = loadConfig('Cycle');
```

### Python

1. Install the library:
```bash
pip install hestia_earth_config
```
2. Import the function to load the configuration:
```python
from hestia_earth.config import load_config

config = load_config('Cycle')
```

If you are using the orchestrator:
```bash
pip install hestia_earth_orchestrator
```
then use in your code:
```python
from hestia_earth.orchestrator import run
from hestia_earth.config import load_config

node = {'@type': 'Cycle'}
config = load_config(node['@type'])
run(node, configuration=config)
```
