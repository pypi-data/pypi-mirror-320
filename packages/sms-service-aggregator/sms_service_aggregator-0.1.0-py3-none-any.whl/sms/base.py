from abc import ABC, abstractmethod
from typing import Optional

class BaseSmsProvider(ABC):
    """短信服务提供商的抽象基类"""
    
    @abstractmethod
    def send_sms(self, phone_number: str, template_id: str, template_params: dict) -> dict:
        """使用模板发送短信的抽象方法"""
        pass
    
    def send_raw_sms(self, phone_number: str, content: str) -> dict:
        """
        直接发送短信内容的方法
        
        Args:
            phone_number: 接收短信的手机号
            content: 短信内容
            
        Returns:
            dict: 发送结果
        """
        raise NotImplementedError("This provider doesn't support sending raw SMS") 