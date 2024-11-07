from flask import Flask, jsonify, request,send_file,send_from_directory
from flask_cors import cross_origin
import jwt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_sockets import Sockets
import datetime
import tool.showflakes as showflakes #雪花ID
from tool.UserMenagement  import Users
from pathlib import Path
import whisper
from Qwen.Qwen.get_chat import QwenChatModel
#import redis

#定时

#from datetime import datetime
from threading import Timer
import time

email_or_phone_code={}
def code_clean_task(item):
    del email_or_phone_code[item]

app = Flask(__name__,static_folder='', static_url_path='')
sockets = Sockets(app)


# jwt1.配置 JWT 密钥
app.config['JWT_SECRET_KEY'] = 'fugubiadeweixinwendaxiaochengxu'  # 用于签名令牌的密钥
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(minutes=30) #改有效期
# jwt2.初始化 JWTManager
jwt_Manager = JWTManager(app)
jwt_Manager.init_app(app)

#
#redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

# 生成随机验证码的函数
def generate_random_code(length=6):
    import random
    return ''.join([str(random.choice(range(10))) for i in range(length)])

import numpy as np

import opencc  #繁体转简体
#获取语音
@app.route("/audio",methods=['GET','POST'])
def GetAudio():
    #Bug 没有传送history  
    # 获取上传的音频数据
    data = request.get_data()  # type: bytes

    with open('output3.mp3', 'wb') as f:
        f.write(data)  # 将音频数据写入文件
    
    # 进行语音识别
    result = whisper_model.transcribe('output3.mp3')  # 传入音频数据
    cc = opencc.OpenCC("t2s")
    res = cc.convert(result['text'])

    
    response,history=model.QwenChat(res,history=[])
    return jsonify({"text":res,"res":response}), 200


#用户通过路由访问图片
@app.route('/images/<filename>')
@cross_origin() 
def image(filename):
    return send_from_directory('images', filename)

import torch
from torchvision import transforms
from PIL import Image
#获取上传图片
@app.route("/upimage",methods=['POST'])
@jwt_required()
def GetImage():
    """
    接收一个Arraybuffer 类型的图片
    """
    file = request.files["file"]
    ID = request.form["ID"]
    user_dir = Path(f'userID/{ID}')
    if not user_dir.exists():
        user_dir.mkdir(parents=True, exist_ok=True)
    if file:
        file_path = user_dir / 'upload/image'
        if not Path(file_path).exists():
            Path(file_path).mkdir(parents=True, exist_ok=True)
        file.save(file_path / 'upimage.png')

        

        # 指定设备
        device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

        # 加载保存的模型实例
        model = torch.load('Densenet201.pth', map_location=device)

        # 确保模型在评估模式
        model.eval()

        # 图片预处理
        def transform_image(image_path):
            image = Image.open(image_path).convert('RGB')  # 确保是RGB格式
            transform = transforms.Compose([
                transforms.Resize((512, 512)),
                transforms.ToTensor(),
                transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
            ])
            image = transform(image).unsqueeze(0)  # 增加一个批次维度
            return image

        # 读取图片并预处理
        image_path = file_path / 'upimage.png'  # 替换为图片路径
        input_image = transform_image(image_path).to(device)

        # 预测图片
        with torch.no_grad():
            outputs = model(input_image)
            _, predicted = torch.max(outputs, 1)

        # 输出预测结果
        #predicted_class = class_names[predicted.item()]
        print(f'Predicted class: {predicted.item()}')
        if predicted.item()==0:
            return 'http://127.0.0.1:9099/static/0.jpg', 200
        else:
            return 'http://127.0.0.1:9099/static/1.jpg', 200
    else:
            print('没有文件！')

    
    return 'http://127.0.0.1:9099/static/-1.jpg', 200

@app.route('/',methods=['POST'])
def login():
    data=request.json
    username=data["nickname"]
    password=data['password']
    if data is None:
            return  jsonify({"code":1,"msg":"登录信息为空"})
    #用户判断
    user=Users()
    if not username or not password:
        return jsonify({"code":0,"msg":"手机或密码为空"})
    login_data=user.login(username,password)
    if login_data["code"]==0:
        return jsonify(login_data) 

    
    # 验证成功
    
    #生成令牌
    user_info={i: j for i, j in login_data["data"].items() if j is not None}#token生成所需的参数字典
    token=create_access_token(identity=user_info)
    login_data["data"]["token"]=token
    return jsonify(login_data)

@app.route("/register", methods=['POST'])
def register():
    data = request.json  # 字典 键名要求一致
    userinfo=data["user"]
    PhoneCode=data["PhoneCode"]
    #有验证码 则验证，补全没有验证码则不验证BUG，需要前端判断是否需要验证
    if PhoneCode:
        if userinfo["nickname"] not in email_or_phone_code:
            return jsonify({"code":0,"msg":"验证码已过期!"})
        if PhoneCode !=email_or_phone_code[userinfo["nickname"]]:
            return jsonify({"code":0,"msg":"短信验证失败"})

    user = Users()
    
    # 雪花ID
    generator = showflakes.SnowflakeIdGenerator()
    snowflake_id = generator.next_id()
    regis_user = {}
    regis_user["ID"] = str(snowflake_id)
    for key, item in userinfo.items():  # 使用.items()来遍历字典
        regis_user[key] = item
    result = user.add(**regis_user)  # 使用**来解包字典作为关键字参数
    user.close()
    return jsonify(result)


@app.route("/phonecode")
#模拟运营商 发送验证码 
def phonecode():
    phone_number= request.args.get('phone')
     # 生成验证码
    code = generate_random_code()
    email_or_phone_code[phone_number]=code

    # 60秒后删除
    Timer(60, code_clean_task, phone_number).start()
    
    # 发送短信的逻辑...
    return jsonify({"phone_code":code}),200  #正常情况不返回验证码，但是我实际没有使用腾讯手机号服务，所以我需要知道这个随机假号码

#------------------------------------------------------------------------------------------------------------------------

#from Qwen.Qwen.Qwen_chat_api import chat_with_model,Chat_with_models_memories

@sockets.route('/chat')
def echo_socket(ws):
    while not ws.closed:
        jsondata = ws.receive() 
        print("监听成功")
        dictdata=eval(jsondata)
        message=dictdata["msg"]
        history=dictdata["history"]
        print(message)
        print(history)

        if not history:
             response,history=model.QwenChat(message,history=[])
        else:
             history=eval(history)
             response,history=model.QwenChat(message,history=history)
        ws.send(response)





@app.route("/tokentest", methods=['POST'])
@jwt_required()
def tokentest():
    # 访问当前用户的 ID
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200

if __name__ == '__main__':
    from gevent import pywsgi
    from geventwebsocket.handler import WebSocketHandler

    model = QwenChatModel()
    whisper_model = whisper.load_model("small.pt")
    server = pywsgi.WSGIServer(('127.0.0.1', 9099), app, handler_class=WebSocketHandler)
    server.serve_forever()


    #app.run(debug=True)