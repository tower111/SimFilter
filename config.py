import os

objPath="/home/yuqing/Desktop/10t-net/tower/PaperProject/SimFilter/"


trainResult=objPath+"/data/trainResult/"


DataSetList=objPath+"/data/GhidraSlience/BinarySim/project/out_filename.json"

sim=-1#0.4  #相似性阈值


test_vul=True #如果用来测试漏洞，设置为True
datacenter=objPath+"/data/datacenter"
if test_vul==True:
    func_vector_info=datacenter+"/SAFE_XA_busybox_search_funcs_vec.json"  #保存语义向量等函数信息
    KeySlienceInfo_Tested = objPath + "/data/GhidraSlience/TestedFirm/extracted_slience/"
    KeySlienceInfo_vul = objPath + "/data/GhidraSlience/Vul/extracted_slience/"
else:
    func_vector_info = datacenter + "/SAFE_XA_busybox_search_funcs_vec_testset.json"  # 保存语义向量等函数信息
    KeySlienceInfo = objPath + "/data/GhidraSlience/BinarySim/extracted_slience/"


binaryPath=objPath+"/data/GhidraSlience/BinarySim/binary/"

good_dataset=-1 #
"""
good_dataset为-1，过滤一个caller中不包含callee的情况，在这种情况下不收集该caller信息
        good_dataset为0则一个caller中不包含callee，认为比较结果为不相似，方法有较高的精确率，召回率较低
        good_dataset为1则一个caller中不包含callee，认为比较结果为相似，方法有较高召回率，但是精确率较低，
                        在漏洞检测场景中选1最好（只有过了相似性校验的caller才能执行这里）
"""
point_number=4 #结果保留小数

set_threold=0.2 #指定结果为1所占比例
number_threold= 0.2


