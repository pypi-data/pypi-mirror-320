# 短信服务配置
SMS_CONFIG = {
    'aliyun': {
        'access_key_id': 'your_access_key_id',
        'access_key_secret': 'your_access_key_secret',
        'sign_name': 'your_sign_name',
    },
    'tencent': {
        'secret_id': 'your_secret_id',
        'secret_key': 'your_secret_key',
        'sdk_app_id': 'your_sdk_app_id',
        'sign_name': 'your_sign_name',
    },
    'chinamobile': {
        'api_key': 'your_api_key',
        'api_secret': 'your_api_secret',
        'sign_name': 'your_sign_name',
    },
    'generic_http': {
        'api_url': 'https://api.example.com/sms/send',
        'api_key': 'your_api_key',
        'sign_name': 'your_sign_name'
    }
} 