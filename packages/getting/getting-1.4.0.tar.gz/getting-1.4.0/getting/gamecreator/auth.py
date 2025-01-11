import requests
from loguru import logger

def login_pw(username, password):
    """使用账号密码登录GC平台并获取信息"""
    try:
        # 获取token
        url = "https://www.gamecreator.com.cn/index.php/apis/user/passwordlogin"
        json = {"username": username, "password": password}
        response = requests.post(url, json=json)
        response.raise_for_status() 

        data = response.json()
        if data.get("code") != 20000:
            logger.info("登录失败：" + data.get("message", "未知错误"))
            return None

        token = data.get("data", {}).get("token")
        if not token:
            logger.info("未获取到token")
            return None
        
        return login_token(token)

    except requests.exceptions.RequestException as e:
        logger.info(f"请求异常：{e}")
        return None
    except ValueError as e:
        logger.info(f"JSON 解析错误：{e}")
        return None


def login_token(token):
    """使用token登录GC平台并获取信息"""
    try:
        url = "https://www.gamecreator.com.cn/index.php/apis/user/getuserinfo"
        headers = {"Token": token}
        response = requests.get(url, headers=headers)
        response.raise_for_status()  

        data = response.json()
        if data.get("code") != 20000:
            logger.info("获取用户信息失败：" + data.get("message", "未知错误"))
            return None

        return data
        
    except requests.exceptions.RequestException as e:
        logger.info(f"请求异常：{e}")
        return None
    except ValueError as e:
        logger.info(f"JSON 解析错误：{e}")
        return None

def login_code(phone,code):
    """使用手机短信登录GC平台并获取信息"""
    try:
        url = "https://www.gamecreator.com.cn/index.php/apis/user/phonecodelogin"
        json = {"phone": str(phone),"code":str(code)}
        response = requests.post(url, json=json)
        response.raise_for_status() 

        data = response.json()
        if data.get("code") != 20000:
            logger.info("登录失败：" + data.get("message", "未知错误"))
            return None

        token = data.get("data", {}).get("token")
        if not token:
            logger.info("未获取到token")
            return None
        
        return login_token(token)

    except requests.exceptions.RequestException as e:
        logger.info(f"请求异常：{e}")
        return None
    except ValueError as e:
        logger.info(f"JSON 解析错误：{e}")
        return None

def get_level(uid):
    """根据uid获取账号等级"""
    try:
        url = "https://www.gamecreator.com.cn/index.php/apis/redismag/get_user_actives"
        json = {"uid": uid}
        response = requests.post(url, json=json)
        response.raise_for_status()  

        data = response.json()
        if data.get("code") != 20000:
            logger.info("获取用户等级失败：" + data.get("message", "未知错误"))
            return None

        return data.get("data")
        
    except requests.exceptions.RequestException as e:
        logger.info(f"请求异常：{e}")
        return None
    except ValueError as e:
        logger.info(f"JSON 解析错误：{e}")
        return None
