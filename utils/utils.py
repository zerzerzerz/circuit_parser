import random 
import json
import numpy as np
import random
import os
import torch
import pickle
import time


def load_json(path):
    with open(path,'r') as f:
        res = json.load(f)
    return res


def save_json(obj, path:str):
    with open(path, 'w', encoding='utf8') as f:
        json.dump(obj, f, indent=4)


def load_pkl(path):
    with open(path, 'rb') as f:
        res = pickle.load(f)
        return res


def save_pkl(obj, path):
    with open(path, 'wb') as f:
        pickle.dump(obj, f)


def setup_seed(seed = 3407):
    torch.manual_seed(seed)
    np.random.seed(seed)
    random.seed(seed)
    torch.cuda.manual_seed(seed)
    # https://zhuanlan.zhihu.com/p/73711222
    # torch.backends.cudnn.benchmark = True


def get_datetime():
    t = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    return t


class Logger():
    def __init__(self,log_file_path) -> None:
        self.path = log_file_path
        with open(self.path,'w') as f:
            f.write(get_datetime() + "\n")
            print(get_datetime())
        return
    
    def log(self,content):
        content = str(content)
        with open(self.path,'a') as f:
            f.write(content + "\n")
            print(content)
        return


def mkdir(dir):
    if os.path.isdir(dir):
        pass
    else:
        os.makedirs(dir)


if __name__ == "__main__":
    print(get_datetime())