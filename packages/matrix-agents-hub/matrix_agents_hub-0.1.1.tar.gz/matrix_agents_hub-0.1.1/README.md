# Matrix Agents Hub

Matrix Agents Hub 是一个用于管理和与各种 AI agents 交互的 Python 包。

## 安装

```bash
pip install matrix-agents-hub
```

## 使用示例

```python
from matrix_agents_hub import AgentsHub, Agent

# 使用单个 Agent
agent = Agent(
    api_key="your-api-key",
    agent_name="agent-name"
)
response = agent.chat("你好")

# 使用 AgentsHub 管理多个 agents
agents = ["agent1", "agent2"]
hub = AgentsHub(agents)
response = hub.chat("agent1", "你好")

# 获取平台上的所有 agents
platform_agents = hub.get_platform_agents()
```

## 环境变量

- `MATRIX_API_KEY`: API密钥（必需）
- `MATRIX_BASE_URL`: 平台服务器地址（可选，默认为 http://localhost:8099）

## 开发

```bash
# 克隆仓库
git clone https://github.com/yourusername/matrix-agents-hub.git

# 安装开发依赖
pip install -e .

# 运行测试
python -m pytest tests/
```

## License

MIT 