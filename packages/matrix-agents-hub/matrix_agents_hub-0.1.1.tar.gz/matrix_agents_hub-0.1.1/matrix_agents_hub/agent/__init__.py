from typing import Optional, List, Dict
import requests
import os

class Agent:
    def __init__(self, api_key: str, agent_id: Optional[str] = None, agent_name: Optional[str] = None, **kwargs):
        """
        初始化Agent实例
        
        Args:
            api_key (str): API密钥
            agent_id (str, optional): agent的唯一标识符
            agent_name (str, optional): agent的名称
        """
        self.api_key = api_key
        self.base_url = os.getenv("MATRIX_BASE_URL") or kwargs.get('base_url', "http://localhost:8099")
        self.headers = {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json"
        }

        self.agent_id = None
        self.agent_name = None

        if agent_id:
            self.agent_id = agent_id
            self.agent_name = agent_name  # 如果提供了agent_name就使用，否则为None
        elif agent_name:
            self.agent_name = agent_name
            id = self.get_agent_id(self.agent_name)
            if id:
                self.agent_id = id
            else:
                raise ValueError("agent not found")
        else:
            raise ValueError("agent_id or agent_name is required")

    def get_functions_definition(self) -> List[Dict]:
        """
        获取agent的函数定义列表
        
        Returns:
            List[Dict]: 函数定义列表，符合OpenAI函数调用格式
        """
        url = f"{self.base_url}/agent/functions"
        data = {
            "agent_id": self.agent_id
        }
        if self.agent_name:
            data["agent_name"] = self.agent_name
            
        response = requests.post(url, headers=self.headers, json=data)
        if response.status_code != 200:
            raise ValueError(f"获取函数定义失败: {response.text}")
            
        return response.json().get("functions", [])

    def get_prompts(self) -> str:
        """
        获取agent的功能描述
        
        Returns:
            str: agent的功能描述
        """
        url = f"{self.base_url}/agent/prompts"
        data = {
            "agent_id": self.agent_id
        }
        if self.agent_name:
            data["agent_name"] = self.agent_name
            
        response = requests.post(url, headers=self.headers, json=data)
        if response.status_code != 200:
            raise ValueError(f"获取功能描述失败: {response.text}")
            
        return response.json().get("prompts", "")

    def chat(self, content: str) -> dict:
        """
        发送查询请求
        
        Args:
            content (str): 查询内容
            
        Returns:
            dict: 查询响应结果
        """
        url = f"{self.base_url}/chat"
        data = {
            "content": content,
            "agent_id": self.agent_id
        }
        
        # 只有在agent_name存在时才添加到请求数据中
        if self.agent_name:
            data["agent_name"] = self.agent_name
            
        response = requests.post(url, headers=self.headers, json=data)
        
        # 检查响应的内容类型
        if response.headers.get('Content-Type') == 'application/json':
            try:
                return response.json()
            except requests.exceptions.JSONDecodeError:
                raise ValueError("服务器返回的不是有效的JSON格式")
        else:
            raise ValueError("服务器返回的内容类型不是JSON")

    def get_agent_id(self, agent_name: str) -> str:
        """
        获取agent的id
        
        Args:
            agent_name (str): agent的名称
            
        Returns:
            str: agent的id
        """
        url = f"{self.base_url}/agent/get_id"
        data = {
            "agent_name": agent_name
        }
        response = requests.post(url, headers=self.headers, json=data)
        if response.status_code != 200:
            return None
        return response.json()
