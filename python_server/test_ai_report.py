#!/usr/bin/env python3
"""
测试直接调用Dify AI的脚本（流式输出版本）
"""
import json
import requests
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


def test_dify_chat():
    """测试Dify AI聊天功能（流式输出）"""
    # Dify API配置
    dify_url = os.getenv("DIFY_BASE_URL", "https://dify.hetunai.cn/v1") + "/chat-messages"
    api_key = os.getenv("DIFY_API_KEY")
    if not api_key:
        print("❌ DIFY_API_KEY环境变量未设置")
        return
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # 测试数据 - 流式聊天
    test_data = {
        "inputs": {},
        "query": "你好，请介绍一下自己",
        "response_mode": "streaming",
        "conversation_id": "",
        "user": "test_user",
        "files": [],
        "auto_generate_name": False
    }
    
    try:
        print("🤖 开始测试Dify AI流式聊天...")
        print(f"📡 请求URL: {dify_url}")
        print(f"💬 问题: {test_data['query']}")
        print("📺 AI回答: ", end='', flush=True)
        
        response = requests.post(dify_url, json=test_data, headers=headers, stream=True, timeout=30)
        
        if response.status_code == 200:
            # 处理流式响应
            complete_answer = ""
            
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    if line_str.startswith('data: '):
                        try:
                            data = json.loads(line_str[6:])
                            if data.get('event') == 'message':
                                # answer字段本身就是增量文本，直接输出即可
                                incremental_text = data.get('answer', '')
                                if incremental_text:
                                    print(incremental_text, end='', flush=True)
                                    complete_answer += incremental_text
                            elif data.get('event') == 'message_end':
                                break
                        except json.JSONDecodeError:
                            continue
            
            print("\n✅ Dify AI聊天测试成功!")
            return {"answer": complete_answer}
        else:
            print(f"\n❌ Dify AI聊天测试失败! 状态码: {response.status_code}")
            print(f"错误响应: {response.text}")
            return None
            
    except Exception as e:
        print(f"\n💥 测试过程中出现异常: {str(e)}")
        return None


def test_dify_report_generation():
    """测试Dify生成项目报告（流式输出）"""
    # Dify API配置
    dify_url = os.getenv("DIFY_BASE_URL", "https://dify.hetunai.cn/v1") + "/chat-messages"
    api_key = os.getenv("DIFY_API_KEY")
    if not api_key:
        print("❌ DIFY_API_KEY环境变量未设置")
        return
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # 构建报告生成的prompt
    report_prompt = """
请为项目生成一份活动总结报告，项目信息如下：

项目ID: 5318863
项目名称: 台球算法项目
时间范围: 最近一周
报告类型: 活动总结

请生成一份包含以下内容的中文报告：
1. 项目概述
2. 本周活动汇总
3. 主要进展和成果
4. 存在的问题和挑战
5. 下周计划

请用专业、清晰的语言撰写报告。
"""
    
    # 测试数据 - 流式报告生成
    test_data = {
        "inputs": {},
        "query": report_prompt,
        "response_mode": "streaming",
        "conversation_id": "",
        "user": "test_user",
        "files": [],
        "auto_generate_name": False
    }
    
    try:
        print("\n📊 开始测试Dify AI流式报告生成...")
        print(f"📡 请求URL: {dify_url}")
        print("📝 正在生成报告...\n")
        
        response = requests.post(dify_url, json=test_data, headers=headers, stream=True, timeout=60)
        
        if response.status_code == 200:
            # 处理流式响应
            previous_length = 0
            complete_report = ""
            
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    if line_str.startswith('data: '):
                        try:
                            data = json.loads(line_str[6:])
                            if data.get('event') == 'message':
                                # answer字段本身就是增量文本，直接输出即可
                                incremental_text = data.get('answer', '')
                                if incremental_text:
                                    print(incremental_text, end='', flush=True)
                                    complete_report += incremental_text
                            elif data.get('event') == 'message_end':
                                break
                        except json.JSONDecodeError:
                            continue
            
            print("\n\n✅ Dify AI报告生成测试成功!")
            return {"answer": complete_report}
        else:
            print(f"❌ Dify AI报告生成测试失败! 状态码: {response.status_code}")
            print(f"错误响应: {response.text}")
            return None
            
    except Exception as e:
        print(f"💥 测试过程中出现异常: {str(e)}")
        return None


def test_dify_streaming():
    """测试Dify流式响应（优化版）"""
    # Dify API配置
    dify_url = os.getenv("DIFY_BASE_URL", "https://dify.hetunai.cn/v1") + "/chat-messages"
    api_key = os.getenv("DIFY_API_KEY")
    if not api_key:
        print("❌ DIFY_API_KEY环境变量未设置")
        return
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # 测试数据 - 流式响应
    test_data = {
        "inputs": {},
        "query": "请用200字左右介绍一下人工智能的发展历程",
        "response_mode": "streaming",
        "conversation_id": "",
        "user": "test_user",
        "files": [],
        "auto_generate_name": False
    }
    
    try:
        print("\n🌊 开始测试Dify AI流式响应...")
        print(f"📡 请求URL: {dify_url}")
        print(f"💬 问题: {test_data['query']}")
        print("📺 AI回答: ", end='', flush=True)
        
        response = requests.post(dify_url, json=test_data, headers=headers, stream=True, timeout=60)
        
        if response.status_code == 200:
            # 处理流式响应
            complete_answer = ""
            
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    if line_str.startswith('data: '):
                        try:
                            data = json.loads(line_str[6:])
                            if data.get('event') == 'message':
                                # answer字段本身就是增量文本，直接输出即可
                                incremental_text = data.get('answer', '')
                                if incremental_text:
                                    print(incremental_text, end='', flush=True)
                                    complete_answer += incremental_text
                            elif data.get('event') == 'message_end':
                                break
                        except json.JSONDecodeError:
                            continue
            
            print("\n\n✅ 流式响应完成!")
            return {"answer": complete_answer}
        else:
            print(f"\n❌ Dify AI流式响应测试失败! 状态码: {response.status_code}")
            print(f"错误响应: {response.text}")
            return False
            
    except Exception as e:
        print(f"\n💥 流式测试过程中出现异常: {str(e)}")
        return False


if __name__ == "__main__":
    print("🚀 直接测试Dify AI功能")
    print("=" * 50)
    
    # 测试基本聊天功能
    # test_dify_chat()
    
    # 测试报告生成功能
    test_dify_report_generation()
    
    # 测试流式响应功能
    # test_dify_streaming()
    
    print("\n✨ 所有测试完成!")