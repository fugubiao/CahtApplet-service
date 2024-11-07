import cx_Oracle


class Users():
    def __init__(self):
        self.conn = cx_Oracle.connect("FGB_STUDY/fgb@localhost/db11g01")
        self.__cursor = self.conn.cursor()
    def __get_user(self,nickname):
        sql = 'SELECT * FROM applet_users'
        if nickname:
            sql=f"select * from applet_users where nickname='{nickname}' "
        self.__cursor.execute(sql)
        result=self.__cursor.fetchall()
        return result
    def __inser_user(self,tablename,**kwargs):
        columns = ', '.join(kwargs.keys()) #' 'username, password, ID'
        # 构建参数列表
        params = tuple(kwargs.values())#('fugubiao', '202410141705', 1846012338835165184)

        sql = f'''INSERT INTO {tablename} ({columns}) VALUES {params}''' 
        # 这写的真是人才，用元组的括号代替了VALUES的括号
        
        try:
            self.__cursor.execute(sql)
            #self.__cursor.execute(sql, params)
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            return {"code": 0, "msg": ""+str(e)+"Error location:UserMenagement/Users()/__inser_user" }
        return {"code": 1, "msg": "注册成功"}

    def login(self,nickname,password):#登录 后返回除了密码以外的所有信息
        usermsg=self.__get_user(nickname)[0] #验证所有用户名密码
        if  usermsg[2]==password and usermsg[1] == nickname:
            usermsg=usermsg[:2]+usermsg[3:]
            #转为字典
            usermsg=dict(zip(('ID', 'nickname', 'phone', 'email', 'birthdays', 'nobel', 'query_number'), usermsg))
            return {"code":1,"data":usermsg,"msg":"登录成功"}
        return {"code":0,"msg":"用户或者密码不正确"}  
    
    def add(self, **kwargs):
       return self.__inser_user("applet_users",**kwargs)

    def close(self):
        self.__cursor.close()
