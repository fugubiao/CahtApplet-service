from datetime import datetime, timedelta
import jwt

class JWTservice:
    def __init__(self, secret_key):
        self.key = secret_key
        """
        #使用示例
        SECRET_KEY = 'SECRET_KEY'
        your_instance = JWTservice(SECRET_KEY)
        user_info = {
            "ID": "123456",
            "username": "BingFish",
            "email": "user@example.com",
            "phone": "1234567890",
            "birthdays": "1990-01-01"
        }

        # 1.调用函数，传入所有可能的用户信息
        your_instance.get_jwt(**user_info)

        # 2..如果某些信息缺失
        your_instance.get_jwt(ID="123456", username="BingFish")
        
        """
    def get_jwt(self, **kwargs):
        # 设置默认payload
        payload = {
            'exp': datetime.now() + timedelta(minutes=30),  # 令牌过期时间
        }

        # 添加所有提供的参数到payload
        for key, value in kwargs.items():
            payload[key] = value

        encoded_jwt = jwt.encode(payload, self.key, algorithm='HS256')
        return encoded_jwt
    def verify_jwt(self, token):
        try:
            # 尝试解码并验证JWT
            payload = jwt.decode(token, self.key, algorithms=['HS256'])
            return True, payload  # 返回True和解码后的payload
        except jwt.ExpiredSignatureError:
            # 令牌过期错误
            return False, "Expired Signature"
        except jwt.InvalidTokenError:
            # 其他无效令牌错误
            return False, "Invalid Token"