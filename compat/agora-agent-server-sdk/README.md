# agora-agent-server-sdk

This package has been renamed to `agora-agents`.

New projects should install:

```sh
pip install agora-agents
```

This compatibility package re-exports the public API from `agora-agents` to support existing installs during the migration window. The primary import path remains `agora_agent`; you can also import from `agora_agent_server_sdk_compat`:

```python
from agora_agent import Agora, Area
from agora_agent_server_sdk_compat import Agora, Area
```

Maintainers: dual-publish steps live in the repository release workflow, not in the root README.
