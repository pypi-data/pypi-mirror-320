from typing import List, Dict, Any
from .agent import Agent
import os
from common.log import logger
import requests

class AgentsHub:
    def __init__(self, agents_list: List[str]):
        """
        初始化AgentsManager
        :param agents_list: agent名称列表
        """
        self.agents = {}
        self.api_key = os.getenv("MATRIX_API_KEY")
        if not self.api_key:
            raise ValueError("请在环境变量中设置 MATRIX_API_KEY")
            
        self.base_url = os.getenv("MATRIX_BASE_URL", "http://localhost:8099")
            
        for agent_name in agents_list:
            try:
                agent = Agent(api_key=self.api_key, agent_name=agent_name,base_url=self.base_url)
                self.agents[agent_name] = agent
                logger.info(f"Agent {agent_name} 初始化成功")
            except Exception as e:
                logger.error(f"Agent {agent_name} 初始化失败: {str(e)}")
                continue

    #增加一个函数，用于获取所有agent的名称
    def get_platform_agents(self) -> List[Dict]:
        """
        获取平台上所有可用的agents信息
        
        Returns:
            List[Dict]: agents信息列表，每个agent包含id、name和description
        """
        try:
            url = f"{self.base_url}/agent/list"
            response = requests.get(
                url,
                headers={
                    "X-API-Key": self.api_key,
                    "Content-Type": "application/json"
                }
            )
            
            if response.status_code != 200:
                raise ValueError(f"获取agents列表失败: {response.text}")
            
            data = response.json()
            if "error" in data:
                raise ValueError(f"获取agents列表失败: {data['error']}")
                
            return data.get("agents", [])
        except Exception as e:
            logger.error(f"获取agents列表失败: {str(e)}")
            return []

    def register(self, agent_name: str) -> bool:
        """
        注册新的agent
        :param agent_name: agent名称
        :return: 注册是否成功
        """
        if agent_name in self.agents:
            logger.warning(f"Agent {agent_name} 已存在")
            return False
        
        try:
            agent = Agent(api_key=self.api_key, agent_name=agent_name)
            self.agents[agent_name] = agent
            logger.info(f"Agent {agent_name} 注册成功")
            return True
        except Exception as e:
            logger.error(f"Agent {agent_name} 注册失败: {str(e)}")
            return False

    def unregister(self, agent_name: str) -> bool:
        """
        注销指定agent
        :param agent_name: agent名称
        :return: 注销是否成功
        """
        if agent_name not in self.agents:
            logger.warning(f"Agent {agent_name} 不存在")
            return False
        
        try:
            del self.agents[agent_name]
            logger.info(f"Agent {agent_name} 注销成功")
            return True
        except Exception as e:
            logger.error(f"Agent {agent_name} 注销失败: {str(e)}")
            return False

    def get_functions_definition(self) -> List[Dict]:
        """
        获取所有agents的函数定义
        :return: 函数定义列表
        """
        functions = []
        for agent_name, agent in self.agents.items():
            agent_functions = agent.get_functions_definition()
            if agent_functions:
                functions.extend(agent_functions)
        return functions

    def get_prompts(self) -> str:
        """
        获取所有agents的功能描述
        :return: 功能描述字符串
        """
        prompts = []
        for agent_name, agent in self.agents.items():
            agent_prompt = f"Agent '{agent_name}' 功能描述:\n"
            agent_prompt += f"{agent.get_description()}\n"
            prompts.append(agent_prompt)
        return "\n".join(prompts)

    def chat(self, agent_name: str, chat_content: str) -> str:
        """
        与指定agent进行对话
        :param agent_name: agent名称
        :param chat_content: 对话内容
        :return: agent响应
        """
        if agent_name not in self.agents:
            raise ValueError(f"Agent {agent_name} 不存在")
        
        response = self.agents[agent_name].chat(chat_content)
        return response.get("response_content", "无响应内容")

    def call(self, agent_name: str, function_name: str, param: Dict[str, Any]) -> Any:
        """
        调用指定agent的特定函数
        :param agent_name: agent名称
        :param function_name: 函数名称
        :param param: 函数参数
        :return: 函数调用结果
        """
        if agent_name not in self.agents:
            raise ValueError(f"Agent {agent_name} 不存在")
        
        return self.agents[agent_name].call(function_name, param) 
    
__version__ = "0.1.0"
__all__ = ["AgentsHub"] 