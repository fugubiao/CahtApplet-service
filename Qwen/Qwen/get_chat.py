import os
from argparse import ArgumentParser
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from transformers.generation import GenerationConfig

DEFAULT_CKPT_PATH = 'Qwen/Qwen/Qwen-1_8B-Chat-48700'

#这个脚本只支持命令行聊天，如果想要调用api 请import Qwen_chat_api
class QwenChatModel:
    def __init__(self, checkpoint_path=DEFAULT_CKPT_PATH, cpu_only=False):
        self.checkpoint_path = checkpoint_path
        self.cpu_only = cpu_only
        self.device = 'cpu' if self.cpu_only else 'cuda'
        self.model, self.tokenizer, self.config = self._load_model_tokenizer()
        self.history=[]
    def _load_model_tokenizer(self):
        tokenizer = AutoTokenizer.from_pretrained(
            self.checkpoint_path, trust_remote_code=True
        )

        if self.cpu_only:
            device_map = "cpu"
        else:
            device_map = "auto"

        model = AutoModelForCausalLM.from_pretrained(
            self.checkpoint_path,
            device_map=device_map,
            trust_remote_code=True
        ).eval().to(self.device)

        config = GenerationConfig.from_pretrained(
            self.checkpoint_path, trust_remote_code=True
        )

        return model, tokenizer, config
    def QwenChat(self,text,history):
        """
        - text:输入文本，type:str
        - history:对话记录 type:list(tuple)  
            例如[('你好。我要入住','好的，请你出示身份证件。'),('我预定的房间','以及看到您预定了我们的302房间，祝你休息愉快！')]
        """
        response, history = self.model.chat(self.tokenizer, text, history=self.history)
        self.history+=history
        return response, self.history
    '''
    只是一次性调用模型的响应，并不带有记忆——history
    '''
    def generate_response(self, input_text):
        inputs = self.tokenizer(input_text, return_tensors="pt").to(self.device)
        with torch.no_grad():
            outputs = self.model.generate(**inputs, generation_config=self.config)
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return response
    
    '''
    自动记忆模型的响应——history
    '''
    def predict(self,_query, _chatbot, _task_history):
        print(f"User: {_query}")
        _chatbot.append((_query, ""))
        full_response = ""

        for response in self.model.chat_stream(self.tokenizer, _query, history=_task_history, generation_config=self.config):
            _chatbot[-1] =(_query, response)

            yield _chatbot
            full_response = response

        print(f"History: {_task_history}")
        _task_history.append((_query, full_response))
        print(f"Qwen-Chat: {full_response}")
   
    def predict_inhistory(self,_query, _task_history,traverse=False):
         
         """
        不自动,可读取静态历史_task_history的模型的响应
        输入查询和历史记忆：
        Keyword Arguments:
            - _query -- 查询文本
            - _task_history -- 历史记录 (default: [])
            - traverse 是否遍历输出
        yield:
            response -- 响应回答

         """
        
         #不遍历
         if not traverse:
            return self.model.chat_stream(self.tokenizer, _query, history=_task_history, generation_config=self.config)

         #不遍历
         for response in self.model.chat_stream(self.tokenizer, _query, history=_task_history, generation_config=self.config):
            yield response

             
            

            


def main():
    parser = ArgumentParser()
    parser.add_argument("-c", "--checkpoint-path", type=str, default=DEFAULT_CKPT_PATH,
                        help="Checkpoint name or path, default to %(default)r")
    parser.add_argument("--cpu-only", action="store_true", help="Run with CPU only")
    args = parser.parse_args()

    model = QwenChatModel(checkpoint_path=args.checkpoint_path, cpu_only=args.cpu_only)
    '''
    predict 记忆问答调用

    chatbot=[]
    task_history=[]
    while True:
        input_text = input("User: ")
        response=model.predict(input_text,chatbot,task_history)

    '''
    ''' generate_response 一次性问答调用 '''
    while True:
        input_text = input("User: ")
        if input_text.lower() in ['exit', 'quit']:
            break
        response = model.generate_response(input_text)
        print(f"Qwen: {response}")



if __name__ == '__main__':
    main()
