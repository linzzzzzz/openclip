"""
Qwen API Client - Sample implementation for interacting with Qwen API
"""

import json
import requests
from typing import Dict, List, Optional, Any
import os
from dataclasses import dataclass


@dataclass
class QwenMessage:
    """Represents a message in the conversation"""
    role: str  # "system", "user", or "assistant"
    content: str


class QwenAPIClient:
    """Client for interacting with Qwen API"""
    
    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"):
        """
        Initialize Qwen API client
        
        Args:
            api_key: Your Qwen API key (can also be set via QWEN_API_KEY env var)
            base_url: Base URL for Qwen API
        """
        self.api_key = api_key or os.getenv("QWEN_API_KEY")
        self.base_url = base_url
        
        if not self.api_key:
            raise ValueError("API key is required. Set QWEN_API_KEY environment variable or pass api_key parameter.")
    
    def _make_request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Make HTTP request to Qwen API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(self.base_url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"API request failed: {e}")
    
    def chat_completion(
        self,
        messages: List[QwenMessage],
        model: str = "qwen-turbo",
        max_tokens: int = 8192,
        temperature: float = 0.7,
        top_p: float = 0.8,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Generate chat completion using Qwen API
        
        Args:
            messages: List of conversation messages
            model: Model to use (qwen-turbo, qwen-plus, qwen-max, etc.)
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0 to 2.0)
            top_p: Top-p sampling parameter
            stream: Whether to stream the response
            
        Returns:
            API response dictionary
        """
        payload = {
            "model": model,
            "input": {
                "messages": [{"role": msg.role, "content": msg.content} for msg in messages]
            },
            "parameters": {
                "max_tokens": max_tokens,
                "temperature": temperature,
                "top_p": top_p,
                "incremental_output": stream
            }
        }
        
        return self._make_request(payload)
    
    def simple_chat(self, prompt: str, model: str = "qwen-turbo") -> str:
        """
        Simple chat interface - send a prompt and get response
        
        Args:
            prompt: User prompt/question
            model: Model to use
            
        Returns:
            Generated response text
        """
        messages = [QwenMessage(role="user", content=prompt)]
        response = self.chat_completion(messages, model=model)
        
        try:
            return response["output"]["text"]
        except KeyError:
            raise Exception(f"Unexpected response format: {response}")
    
    def conversation_chat(
        self,
        messages: List[QwenMessage],
        system_prompt: Optional[str] = None,
        model: str = "qwen-turbo"
    ) -> str:
        """
        Multi-turn conversation chat
        
        Args:
            messages: List of conversation messages
            system_prompt: Optional system prompt to set context
            model: Model to use
            
        Returns:
            Generated response text
        """
        conversation = []
        
        if system_prompt:
            conversation.append(QwenMessage(role="system", content=system_prompt))
        
        conversation.extend(messages)
        
        response = self.chat_completion(conversation, model=model)
        
        try:
            return response["output"]["text"]
        except KeyError:
            raise Exception(f"Unexpected response format: {response}")


def main():
    """Example usage of Qwen API client"""
    
    # Initialize client (make sure to set QWEN_API_KEY environment variable)
    try:
        client = QwenAPIClient()
    except ValueError as e:
        print(f"Error: {e}")
        print("Please set your QWEN_API_KEY environment variable")
        return
    
    print("=== Qwen API Client Demo ===\n")
    
    # Example 1: Simple chat
    print("1. Simple Chat Example:")
    try:
        response = client.simple_chat("Hello! Can you tell me about artificial intelligence?")
        print(f"Response: {response}\n")
    except Exception as e:
        print(f"Error: {e}\n")
    
    # Example 2: Conversation with system prompt
    print("2. Conversation with System Prompt:")
    try:
        system_prompt = "You are a helpful assistant that specializes in explaining technical concepts clearly."
        messages = [
            QwenMessage(role="user", content="What is machine learning?"),
        ]
        
        response = client.conversation_chat(messages, system_prompt=system_prompt)
        print(f"Response: {response}\n")
    except Exception as e:
        print(f"Error: {e}\n")
    
    # Example 3: Multi-turn conversation
    print("3. Multi-turn Conversation:")
    try:
        messages = [
            QwenMessage(role="user", content="What is Python?"),
            QwenMessage(role="assistant", content="Python is a high-level programming language known for its simplicity and readability."),
            QwenMessage(role="user", content="Can you give me a simple Python example?")
        ]
        
        response = client.conversation_chat(messages)
        print(f"Response: {response}\n")
    except Exception as e:
        print(f"Error: {e}\n")
    
    # Example 4: Different models and parameters
    print("4. Using Different Model and Parameters:")
    try:
        messages = [QwenMessage(role="user", content="Write a short poem about technology")]
        response = client.chat_completion(
            messages,
            model="qwen-plus",  # Using a different model
            temperature=0.9,    # Higher creativity
            max_tokens=200
        )
        print(f"Response: {response['output']['text']}\n")
    except Exception as e:
        print(f"Error: {e}\n")


if __name__ == "__main__":
    main()