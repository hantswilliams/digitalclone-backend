import os 
import torch
import cv2

def test():

    var1=os.getenv('ENV_VAR_1')
    var2=os.getenv('ENV_VAR_2')

    # print version of cv2
    print(cv2.__version__)
    # print version of torch
    print(torch.__version__)

    print('var1: ', var1)
    print('var2: ', var2)

    cmd = r'ffmpeg '
    os.system(cmd)

if __name__ == '__main__':
    test()