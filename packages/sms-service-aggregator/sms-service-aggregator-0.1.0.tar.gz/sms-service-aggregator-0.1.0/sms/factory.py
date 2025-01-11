from .providers.aliyun import AliyunSmsProvider
from .providers.tencent import TencentSmsProvider
from .providers.chinamobile import ChinaMobileSmsProvider
from .providers.generic_http import GenericHttpProvider

class SmsFactory:
    """短信服务工厂类"""
    
    @staticmethod
    def create_provider(provider_name: str):
        """
        创建短信服务提供商实例
        
        Args:
            provider_name: 提供商名称 (aliyun/tencent/chinamobile)
            
        Returns:
            BaseSmsProvider: 短信服务提供商实例
        """
        providers = {
            'aliyun': AliyunSmsProvider,
            'tencent': TencentSmsProvider,
            'chinamobile': ChinaMobileSmsProvider,
            'generic_http': GenericHttpProvider
        }
        
        provider_class = providers.get(provider_name.lower())
        if not provider_class:
            raise ValueError(f"Unsupported SMS provider: {provider_name}")
        
        return provider_class() 