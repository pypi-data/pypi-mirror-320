import json
import subprocess
from typing import Dict, Any, List, Optional, Tuple

import yaml
from .tools import ToolRegistry
from .utils import PrettyOutput, OutputType, get_multiline_input
from .models import BaseModel
import re
import os
from datetime import datetime

class Agent:
    def __init__(self, model: BaseModel, tool_registry: ToolRegistry, name: str = "Jarvis", is_sub_agent: bool = False):
        """Initialize Agent with a model, optional tool registry and name
        
        Args:
            model: 语言模型实例
            tool_registry: 工具注册表实例
            name: Agent名称，默认为"Jarvis"
            is_sub_agent: 是否为子Agent，默认为False
        """
        self.model = model
        self.tool_registry = tool_registry or ToolRegistry(model)
        self.name = name
        self.is_sub_agent = is_sub_agent
        self.messages = []


    @staticmethod
    def extract_tool_calls(content: str) -> List[Dict]:
        """从内容中提取工具调用，如果检测到多个工具调用则抛出异常，并返回工具调用之前的内容和工具调用"""
        # 分割内容为行
        lines = content.split('\n')
        tool_call_lines = []
        in_tool_call = False
        
        # 逐行处理
        for line in lines:
            if '<START_TOOL_CALL>' in line:
                in_tool_call = True
                continue
            elif '<END_TOOL_CALL>' in line:
                if in_tool_call and tool_call_lines:
                    try:
                        # 直接解析YAML
                        tool_call_text = '\n'.join(tool_call_lines)
                        tool_call_data = yaml.safe_load(tool_call_text)
                        
                        # 验证必要的字段
                        if "name" in tool_call_data and "arguments" in tool_call_data:
                            # 返回工具调用之前的内容和工具调用
                            return [{
                                "name": tool_call_data["name"],
                                "arguments": tool_call_data["arguments"]
                            }]
                        else:
                            PrettyOutput.print("工具调用缺少必要字段", OutputType.ERROR)
                            raise '工具调用缺少必要字段'
                    except yaml.YAMLError as e:
                        PrettyOutput.print(f"YAML解析错误: {str(e)}", OutputType.ERROR)
                        raise 'YAML解析错误'
                    except Exception as e:
                        PrettyOutput.print(f"处理工具调用时发生错误: {str(e)}", OutputType.ERROR)
                        raise '处理工具调用时发生错误'
                in_tool_call = False
                continue
            
            if in_tool_call:
                tool_call_lines.append(line)
        
        return []

    def _call_model(self, messages: List[Dict]) -> Dict:
        """调用模型获取响应"""
        try:
            return self.model.chat(
                messages=messages,
            )
        except Exception as e:
            raise Exception(f"{self.name}: 模型调用失败: {str(e)}")

    def run(self, user_input: str) -> str:
        """处理用户输入并返回响应，返回任务总结报告"""
        self.clear_history()
        
        # 显示任务开始
        PrettyOutput.section(f"开始新任务: {self.name}", OutputType.PLANNING)

        tools_prompt = "可用工具:\n"
        for tool in self.tool_registry.get_all_tools():
            tools_prompt += f"- 名称: {tool['name']}\n"
            tools_prompt += f"  描述: {tool['description']}\n"
            tools_prompt += f"  参数: {tool['parameters']}\n"

        self.messages = [
            {
                "role": "user",
                "content": f"""你是 {self.name}，一个严格遵循 ReAct 框架进行逐步推理和行动的 AI 助手。

{tools_prompt}

关键规则：
‼️ 禁止创建虚假对话
‼️ 禁止假设用户回应
‼️ 禁止在没有实际用户输入时继续
‼️ 只回应用户实际说的内容
‼️ 每个动作后停止并等待

ReAct 框架：
1. 思考
   - 分析当前情况
   - 考虑可用工具
   - 规划下一步行动
   - 仅基于事实
   - 不做用户回应的假设
   - 不想象对话内容

2. 行动（可选）
   - 不是每次回应都需要调用工具
   - 如果需要更多信息，直接询问用户
   - 使用工具时：
     - 只使用下面列出的工具
     - 每次只执行一个工具
     - 工具由用户手动执行
     - 必须使用有效的YAML格式：
     <START_TOOL_CALL>
     name: tool_name
     arguments:
         param1: value1       # 所有参数必须正确缩进
         param2: |           # 使用YAML块样式表示多行字符串
             line1
             line2
     <END_TOOL_CALL>

3. 观察
   - 等待工具执行结果或用户回应
   - 工具执行结果由用户提供
   - 不要假设或想象回应
   - 不要创建虚假对话
   - 停止并等待实际输入

回应格式：
思考：我分析当前情况[具体情况]... 基于[事实]，我需要[目标]...

[如果需要使用工具：]
行动：我将使用[工具]来[具体目的]...
<START_TOOL_CALL>
name: tool_name
arguments:
    param1: value1
    param2: |
        multiline
        value
<END_TOOL_CALL>

[如果需要更多信息：]
我需要了解更多关于[具体细节]的信息。请提供[需要的信息]。

严格规则：
‼️ 只使用下面列出的工具
‼️ 工具调用是可选的 - 需要时询问用户
‼️ 每次只能调用一个工具
‼️ 工具调用必须是有效的YAML格式
‼️ 参数必须正确缩进
‼️ 使用YAML块样式(|)表示多行值
‼️ <END_TOOL_CALL>后的内容将被丢弃
‼️ 工具由用户手动执行
‼️ 等待用户提供工具执行结果
‼️ 不要假设或想象用户回应
‼️ 没有用户输入时不要继续对话
‼️ 不要创建虚假对话
‼️ 每个动作后停止
‼️ 不要假设结果
‼️ 不要假设行动

注意事项：
- 先思考再行动
- 需要时询问用户
- 只使用列出的工具
- 一次一个工具
- 严格遵循YAML格式
- 等待用户回应
- 工具结果来自用户
- 不要假设回应
- 不要虚构对话
- 每个动作后停止
- 只在有实际用户输入时继续

任务:
{user_input}
"""
            }
        ]
        
        while True:
            try:
                # 显示思考状态
                PrettyOutput.print("分析任务...", OutputType.PROGRESS)
                
                current_response = self._call_model(self.messages)

                try:
                    result = Agent.extract_tool_calls(current_response)
                except Exception as e:
                    PrettyOutput.print(f"工具调用错误: {str(e)}", OutputType.ERROR)
                    self.messages.append({
                        "role": "user",
                        "content": f"工具调用错误: {str(e)}"
                    })
                    continue


                self.messages.append({
                    "role": "assistant",
                    "content": current_response
                })

                
                if len(result) > 0:
                    try:
                        # 显示工具调用
                        PrettyOutput.print("执行工具调用...", OutputType.PROGRESS)
                        tool_result = self.tool_registry.handle_tool_calls(result)
                        PrettyOutput.print(tool_result, OutputType.RESULT)
                    except Exception as e:
                        PrettyOutput.print(str(e), OutputType.ERROR)
                        tool_result = f"Tool call failed: {str(e)}"

                    self.messages.append({
                        "role": "user",
                        "content": tool_result
                    })
                    continue
                
                # 获取用户输入
                user_input = get_multiline_input(f"{self.name}: 您可以继续输入，或输入空行结束当前任务")
                if not user_input:
                    # 只有子Agent才需要生成任务总结
                    if self.is_sub_agent:
                        PrettyOutput.print("生成任务总结...", OutputType.PROGRESS)
                        
                        # 生成任务总结
                        summary_prompt = {
                            "role": "user",
                            "content": """任务已完成。请根据之前的分析和执行结果，提供一个简明的任务总结，包括：

1. 关键发现：
   - 分析过程中的重要发现
   - 工具执行的关键结果
   - 发现的重要数据

2. 执行成果：
   - 任务完成情况
   - 具体实现结果
   - 达成的目标

请直接描述事实和实际结果，保持简洁明了。"""
                        }
                        
                        while True:
                            try:
                                summary = self._call_model(self.messages + [summary_prompt])
                                 
                                # 显示任务总结
                                PrettyOutput.section("任务总结", OutputType.SUCCESS)
                                PrettyOutput.print(summary, OutputType.SYSTEM)
                                PrettyOutput.section("任务完成", OutputType.SUCCESS)
                                
                                return summary
                                
                            except Exception as e:
                                PrettyOutput.print(str(e), OutputType.ERROR)
                    else:
                        # 顶层Agent直接返回空字符串
                        PrettyOutput.section("任务完成", OutputType.SUCCESS)
                        return ""
                
                if user_input == "__interrupt__":
                    PrettyOutput.print("任务已取消", OutputType.WARNING)
                    return "Task cancelled by user"
                
                self.messages.append({
                    "role": "user",
                    "content": user_input
                })
                
            except Exception as e:
                PrettyOutput.print(str(e), OutputType.ERROR)

    def clear_history(self):
        """清除对话历史，只保留系统提示"""
        self.messages = [] 
        self.model.reset()
