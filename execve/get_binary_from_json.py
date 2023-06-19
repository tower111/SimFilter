import json
import os
from shutil import copyfile
from tqdm import tqdm


json_path="/home/yuqing/Desktop/10t-net/tower/PaperProject/SimFilter/data/GhidraSlience/BinarySim/project/out_filename.json"
input_pathp="/home/yuqing/Desktop/10t-net/近期项目/NeroMain_new/test_py/data/train_file/lto_dataset/gnu_debug_lto/"
output_path="/home/yuqing/Desktop/10t-net/tower/PaperProject/SimFilter/data/GhidraSlience/BinarySim/binary/"

def runcmd(cmd):
    result = os.popen(cmd)
    res = result.read()
    assert (len(res.splitlines())==1)
    for line in res.splitlines():
        return line

with open(json_path,"r") as fd:
    filelist=json.loads(fd.read())

def getsource(name):
    realpath=runcmd("find {} |grep {}".format(input_path,name))
    return realpath
result={}
for file in tqdm(filelist):
    name=os.path.basename(file)
    outfile=output_path+"/"+name
    inputfile=getsource(name)
    result[inputfile]=outfile
    # print(inputfile,outfile)
    copyfile(inputfile, outfile)
with open(json_path,"w") as fd:
    fd.write(json.dumps(result))