import os

objPath="/home/yuqing/Desktop/10t-net/tower/PaperProject/SimFilter/"


trainResult=objPath+"/data/trainResult/"

KeySlienceInfo=objPath+"/KeySlience/ghidra_engine/my_script/out/indexed/"
DataSetList=objPath+"/KeySlience/ghidra_engine/my_script/out/project/out_filename.json"

sim=0.4  #相似性阈值
datacenter=objPath+"/data/datacenter"
func_vector_info=datacenter+"/SAFE_XA_busybox_search_funcs_vec.json"  #保存语义向量等函数信息


binaryPath=objPath+"/KeySlience/ghidra_engine/my_script/out/binary/"

good_dataset=1 #
"""
good_dataset为-1，过滤一个caller中不包含callee的情况，在这种情况下不收集该caller信息
        good_dataset为0则一个caller中不包含callee，认为比较结果为不相似，方法有较高的精确率，召回率较低
        good_dataset为1则一个caller中不包含callee，认为比较结果为相似，方法有较高召回率，但是精确率较低，
                        在漏洞检测场景中选1最好（只有过了相似性校验的caller才能执行这里）
"""