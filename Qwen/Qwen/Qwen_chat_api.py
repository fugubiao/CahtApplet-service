from argparse import ArgumentParser
#from get_chat import QwenChatModel
from Qwen.Qwen.get_chat import QwenChatModel
'''
QwenChatModelHandler 类用于处理模型的加载和聊天。
在类的初始化过程中加载模型，保证模型只加载一次。
通过 chat 方法与模型交互，用户输入 "exit" 或 "quit" 时会返回退出消息，但不会重启模型。
chat_with_model 函数外部调用模型处理类的方法。
主程序部分包含一个循环，允许用户持续输入问题并获取回答，直到输入 "exit" 或 "quit"。

'''

class QwenChatModelHandler:
    def __init__(self,DEFAULT_CKPT_PATH = 'Qwen/Qwen/Qwen-1_8B-Chat-12200'):
        parser = ArgumentParser()
        parser.add_argument("-c", "--checkpoint-path", type=str, default=DEFAULT_CKPT_PATH,
                            help="Checkpoint name or path, default to %(default)r")
        parser.add_argument("--cpu-only", action="store_true", help="Run with CPU only")
        self.args = parser.parse_args()
        self.model = None
        self.load_model()
        self.task_history = []  # 初始化历史记录

    def load_model(self):
        self.model = QwenChatModel(checkpoint_path=self.args.checkpoint_path, cpu_only=self.args.cpu_only)

    def chat(self, user_input):
        #if user_input.lower() in ['exit', 'quit']:
            #return "Exiting..."

        #response = self.model.predict(user_input,)
        response = self.model.generate_response(user_input)
        return response
    def history_chat(self,input_text,traverse=False):
        return self.model.predict_inhistory(input_text,traverse)

# 创建模型处理类实例
model_handler = QwenChatModelHandler()

def chat_with_model(user_input):
    return model_handler.chat(user_input)
def Chat_with_models_memories(user_input,traverse=False):
    result=model_handler.history_chat(user_input,traverse)
    return result
if __name__ == "__main__":
    while True:
        user_input = input("User: ")
        print(type(user_input))
        response = chat_with_model(user_input)
        print(f"Bot: {response}")
        if response == "Exiting...":
            break
