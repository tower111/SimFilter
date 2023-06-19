import json
import os
import hashlib
from shutil import copyfile
import config

sourcepath="/home/yuqing/Desktop/10t-net/近期项目/NeroMain_new/test_py/data/vul_file/VulFirmware_24/"
targetpath=config.obPath+"/data/GhidraSlience/TestedFirm/binary/"


result={}
def getmd5(filename):
    with open(filename,"rb") as fd:
        content=fd.read()
    md5hash = hashlib.md5(content)
    md5 = md5hash.hexdigest()
    return md5
def is_dangerous(filename):
    firm_list=["RT-AC66U_3.0.0.4_382_52287-g798e87f.trx","RT-AC66U_378.55_0.trx", #CVE-2013-4659
               "R6250-V1.0.4.8_10.1.13.chk","R6250-V1.0.4.38_10.1.30.chk", #CVE-2016-6277
               "routeros-arm-6.42.4.npk","routeros-arm-6.42.5.npk",   #CVE-2018-1156
               "RT-AC3200_3.0.0.4_382_52545-ga0245cc.trx","RT-AC3200_9.0.0.4_382_52504-g01bf5f5.trx", #CVE-2018-14712
               ]
    file_end_black_list=[".ko",".so"]
    for item in firm_list:
        if item in filename:
            for end in file_end_black_list:
                if filename.endswith(end):
                    return False
            else:
                if "lib" in os.path.basename(filename):
                    return False
                return True
    return False

for fpathe,dirs,fs in os.walk(sourcepath):
    for f in fs:
        source = os.path.join(fpathe,f)

        # print(source)
        if is_dangerous(source):
            target = targetpath + os.path.basename(f) + "-" + getmd5(source)
            print(source, target)
            copyfile(source, target)
            result[source]=target
        else:
            pass
with open(targetpath+"result.json","w") as fd:
    fd.write(json.dumps(result))

