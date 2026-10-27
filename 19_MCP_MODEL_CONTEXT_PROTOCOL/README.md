# Model Context Protocol (MCP)

Chapter notes for **Souvik’s** AI learning journey (folder `19_MCP_MODEL_CONTEXT_PROTOCOL`).

**MCP** is a **standard protocol** for connecting AI applications (hosts) to external **tools**, **data**, and **prompt templates** — without building a custom integration for every pair of app and service.

Read in order **`1_` → `5_`**:

| # | Note | Topic |
|---|------|--------|
| 1 | [`1_introduction.md`](./1_introduction.md) | Why MCP, USB-C analogy, what MCP is not, tools focus, M×N → M+N |
| 2 | [`2_core_mcp_terminology.md`](./2_core_mcp_terminology.md) | Host, Client, Server |
| 3 | [`3_communication_flow.md`](./3_communication_flow.md) | End-to-end workflow (user → host → client → server) |
| 4 | [`4_the_communication_protocol.md`](./4_the_communication_protocol.md) | JSON-RPC, transport (stdio / HTTP), **interaction lifecycle** |
| 5 | [`5_mcp_capabilities.md`](./5_mcp_capabilities.md) | Tools, Resources, Prompts, Sampling |
| 6 | [`6_fastmcp.md`](./6_fastmcp.md) | FastMCP — Python MCP servers, CLI, Claude Desktop |

### Hands-on projects

| Folder | Files | Topic |
|--------|--------|--------|
| [`PROJECT_1/`](./PROJECT_1/) | [`weather.py`](./PROJECT_1/weather.py) · [`7_weather_py.md`](./PROJECT_1/7_weather_py.md) | NWS MCP **server** + Cursor `mcp.json` (CA / Kolkata examples) |
| [`PROJECT_2/`](./PROJECT_2/) | [`server.py`](./PROJECT_2/server.py) · [`mcp_client.py`](./PROJECT_2/mcp_client.py) · [`test_client.py`](./PROJECT_2/test_client.py) · [`8_mcp_client_lab.md`](./PROJECT_2/8_mcp_client_lab.md) | MCP **client** in Python (`fastmcp.Client`) |
| [`PROJECT_3/`](./PROJECT_3/) | [`server.py`](./PROJECT_3/server.py) · [`mcp_client.py`](./PROJECT_3/mcp_client.py) · [`planner.py`](./PROJECT_3/planner.py) · [`agent.py`](./PROJECT_3/agent.py) · [`9_mcp_agent_lab.md`](./PROJECT_3/9_mcp_agent_lab.md) | **Agent**: LLM planner + MCP tools (Topic 18 pattern on MCP server) |

**Before this chapter**

- Tools in your own Python: [`5_TOOLS_FUNCTIONS/`](../5_TOOLS_FUNCTIONS/)  
- Mini agent (planner + local tools): [`18_AI_AGENTS_INTRO/`](../18_AI_AGENTS_INTRO/)  
- Agents theory: [`agents_and_tools.md`](../6_AGENTS_AND_TOOLS/agents_and_tools.md)

**Official spec (reference):** [modelcontextprotocol.io](https://modelcontextprotocol.io)
