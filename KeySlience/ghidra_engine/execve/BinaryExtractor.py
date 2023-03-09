import os.path
import json
from unittest import result
from utils.llvm_info import *
from utils.file_process import *
from tqdm import tqdm
import ghidra_engine.SimFilterConfig as config
import config_est_py as globalconfig
import hashlib
from utils.Normal_db import Nomal_db

import subprocess
import time


# import test_py.bin.retdec_decompiler as decompiler
def clean():
    """
    清除过程中生成的所有文件
    """
    os.system("rm -rf {}/*".format(config.output_path))#抽取文件结果存放目录
    os.system("rm -rf {}/*".format(config.ghidra_project_path))#ghidra项目存放目录
    os.system("rm -rf {}/*".format(config.save_binary_path))  # 保存的二进制文件存放目录


def init():
    pass
    # # os.system("rm -rf {}".format(config.output_path + ""))
    # Nb = Nomal_db(config.Normolized_database)
    # Nb.create_db()
    # return Nb


def run_cmd(cmd_string, timeout=globalconfig.timeout):
    config.log.debug("命令为：" + cmd_string)
    try:
        p = subprocess.Popen(cmd_string,
                             stderr=subprocess.STDOUT,
                             stdout=subprocess.PIPE,
                             shell=True)
        t_beginning = time.time()
        res_code = 0
        while True:
            if p.poll() is not None:
                break
            seconds_passed = time.time() - t_beginning
            if timeout and seconds_passed > timeout:
                p.terminate()  # 等同于p.kill()
                msg = "Timeout ：Command '" + cmd_string + "' timed out after " + str(
                    timeout) + " seconds"
                raise Exception(msg)
            time.sleep(0.1)

        msg = str(p.stdout.read().decode('utf-8'))
    except Exception as e:
        res_code = 1
        msg = "[ERROR]Unknown Error : " + str(e)
    if "Error: File format of the input file is not supported. Supported formats: PE, ELF, COFF, Mach-O, Intel HEX, Raw Data" in msg:
        res_code = 1
    return res_code, msg

class Extractor:
    def __init__(self):
        self.file_list=[]
    def FileMd5(self,filename):
        with open(filename, 'rb') as fp:
            data = fp.read()
        file_md5 = hashlib.md5(data).hexdigest()
        return file_md5
    def decomplier(self):
        """
        遍历input_path ，
        调用config.decomplier_path里的反编译引擎，
        输出结果到config.output_path目录
        """
        succ_num = 0
        all_num = 0
        for file_name in get_file(config.input_path, trainer=True):

            all_num += 1

            config.log.debug("反编译成功：{}，总数量：{}".format(succ_num, all_num))

            out_put_dir = config.save_binary_path

            out_filename = out_put_dir + "/" + os.path.basename(file_name)

            config.log.debug("文件分析完成：{}".format(file_name))
            os.system("cp {} {}".format(file_name,out_filename))
            assert  os.path.exists(out_filename)
            succ_num += 1
            yield out_filename





    def get_slience(self):
        init()
        succ = 0
        result=[]
        for file_name in tqdm(self.decomplier()):
            succ+=1
            result.append(file_name)
            if succ > 300:
                break
        with open(config.ghidra_project_path+"/out_filename.json","w") as fd:
            fd.write(json.dumps(result))
            # get_func_slience(file_name)
            # succ += 1
            # # ll_file_name=file_name+".ll"
            # pass
if __name__ == "__main__":
    # clean()
    config.log.debug("BinaryExtractor.py")
    extractor=Extractor()
    extractor.get_slience()
    # clean()
