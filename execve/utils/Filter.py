import os
from functools import lru_cache
import config
import ujson
from tqdm import tqdm
import json
class Filter:
    def __init__(self):
        # self.
        # self.binaryList=self.binary()
        # print("loading sl")
        self.all_KeyStatment=[]
        if config.test_vul==False:
            self.SliencePath = config.KeySlienceInfo
            self.SlenceInfo = self.GetslienceInfo(self.SliencePath)
        else:
            self.SliencePath_tested=config.KeySlienceInfo_Tested
            self.SliencePath_vul=config.KeySlienceInfo_vul
            self.SlenceInfo_tested=self.GetslienceInfo(self.SliencePath_tested)
            self.SlenceInfo_vul = self.GetslienceInfo(self.SliencePath_vul)
            self.SlenceInfo={}
            self.SlenceInfo.update(self.SlenceInfo_vul)
            self.SlenceInfo.update(self.SlenceInfo_tested)
            # self.SlenceInfo=dict(self.SlenceInfo_vul.items()+self.SlenceInfo_tested.items())
            # self.SlenceInfo =self.SlenceInfo_tested
        self.filename=set() #保存所有文件名


        self.method_list=["filter_constValue_fine","filter_arrayLen_fine","filter_varType_fine","filter_number_slienceLen_fine",
                          "filter_number_const_fine","filter_number_call_fine","filter_number_var_fine",
                          "filter_number_call_param_fine","filter_num_param_fine"]
        self.method_weight={
            "filter_constValue_fine":1/10,
            "filter_arrayLen_fine":1.5/10,
            "filter_varType_fine" :1.5/10,
            "filter_number_slienceLen_fine":0.5/10,
            "filter_number_const_fine":0.5/10,
            "filter_number_call_fine":1.5/10,
            "filter_number_var_fine":0.5/10,
            "filter_number_call_param_fine":1/10,
            "filter_num_param_fine" :1/10,
            "rawMethod":1/10
        }


    @staticmethod
    def Md5(filename):
        import hashlib
        with open(filename,"rb") as fd:
            md5=hashlib.md5(fd.read()).hexdigest()
        return md5.lower()
    def binary(self):
        with open(config.DataSetList,"r") as fd:
            data=ujson.loads(fd.read())
        result={}

        for item in data:
            basename = os.path.basename(item)
            filename = os.path.join(config.binaryPath, basename)

            result[basename]=self.Md5(filename)
        return result


    def ComSlience_int_fine(self,slience,slience1,content,threshold):
        """
        :param slience:要比较的切片
        :param slience1:
        :param content: 要比较的字段内容
        :param threshold: 比较的阈值
        :return: 是否相似，相似为1，不相似为0
        """

        @lru_cache()
        def preprocess_dict():

            for info in slience:
                for k, v in info.items():
                    if config.test_vul == True:
                        if (k[0].startswith("FUN_")):  # FUN_0007d7ac
                            all_const[("FUN", k[1])] = v
                        else:
                            all_const[k] = v
                    else:
                        all_const[k] = v

            for info in slience1:
                for k, v in info.items():
                    if config.test_vul == True:
                        if (k[0].startswith("FUN_")):  # FUN_0007d7ac
                            all_const1[("FUN", k[1])] = v
                        else:
                            all_const1[k] = v
                    else:
                        all_const1[k] = v

        all_const = dict()
        all_const1 = dict()
        preprocess_dict()
        result_flag=[]
        for callee_name,info in all_const.items():
            if callee_name in all_const1:
                callee_constinfo=all_const[callee_name][content]
                callee_constinfo1 = all_const1[callee_name][content]
                if callee_constinfo==0 and callee_constinfo1==0:
                    result_flag.append(1)
                    continue
                if callee_constinfo==0 or callee_constinfo1==0:
                    result_flag.append(0)
                    continue
                if abs(callee_constinfo-callee_constinfo1)/callee_constinfo<=0 or \
                    abs(callee_constinfo-callee_constinfo1)/callee_constinfo1<=0:
                    result_flag.append(1)
                else:
                    result_flag.append(0)
            else:
                result_flag.append(0)
        # self.all_KeyStatment.append(len(result_flag))#+=len(result_flag)

        if(result_flag.count(1)/len(result_flag))>=threshold:
            return 1
        else:
            return 0



    def GetslienceInfo(self,path):
        result={}
        for file in os.listdir(path):
            if os.path.isdir(file) :
                continue
            # if file in result:
            assert not(file in result)
            if "statistic_extracted" in file:
                with open(path+file,"r") as fd:
                    data=ujson.loads(fd.read())
                if config.test_vul==False:
                    result[file.split(".elf_")[0]+".elf"]=self.preprocess_slienceinfo(data)
                else:
                    file=file.replace("__statistic_extracted.json","")
                    result["_".join(file.split("_")[0:-1]) ] = self.preprocess_slienceinfo(data)
        return result
    def Get_Sim(self):
        info = self.getinfo(config.func_vector_info)
        result={}
        file_info_right={}
        continue_flag=0
        method_list=self.method_list
        def init():
            for method_name in  method_list:
                result[method_name]={"realLable":[],"predictLable":[]}
                file_info_right[method_name]=[]
            result["rawMethod"] = {"realLable": [], "predictLable": []}
            file_info_right["rawMethod"] = []
        def add_allMethod_pred(value):
            for method_name in  method_list:
                result[method_name]["predictLable"].append(value)

        def add_allMethod_label(value):
            for method_name in method_list:
                result[method_name]["realLable"].append(value)
        init()
        for funca,funcb,pred,label in self.GetFuncPair(info):

            #'binutils-2.30_clang-4.0_arm_32_O2_objdump.elf_5ee5d7aff4e46ca78d46c7bcd0d910ab__statistic_extracted.json'
            if funca["file_name"] not in self.SlenceInfo:
                # result["predictLable"].append(-1)
                continue
            if funcb["file_name"] not in self.SlenceInfo:
                # result["predictLable"].append(-1)
                continue

            if pred<config.sim:
                add_allMethod_pred(-1)
                result["rawMethod"]["predictLable"].append(-1)
                # result["predictLable"].append(-1)

            else:#满足相似性约束
                continue_flag = 0
                for method_name,filf in self.filter_slience_info(funca, funcb,config.good_dataset).items():
                    continue_flag=0
                    if filf==1:
                        result[method_name]["predictLable"].append(1)
                        file_info_right[method_name].append(({"vul":(funca["file_name"],funca["fun_name"],
                                                                     funca["fun_address"]),
                                                              "tested":(funcb["file_name"],funcb["fun_name"],
                                                                     funcb["fun_address"])}))
                    elif filf==-1:#获取信息失败
                        continue_flag=1
                        break
                    else:
                        # print(filf)
                        assert filf==0
                        result[method_name]["predictLable"].append(-1)
                if continue_flag==1:
                    continue
                result["rawMethod"]["predictLable"].append(1)
                file_info_right["rawMethod"].append(({"vul": (funca["file_name"], funca["fun_name"],
                                                              funca["fun_address"]),
                                                      "tested": (funcb["file_name"], funcb["fun_name"],
                                                                 funcb["fun_address"])}))
            add_allMethod_label(label)
            result["rawMethod"]["realLable"].append(label)
            self.filename.add(funcb["file_name"])
            self.filename.add(funca["file_name"])
        return result,file_info_right
    @staticmethod
    def getinfo(filename):
        with open(filename, "r") as fd:
            content = ujson.loads(fd.read())
        return content
    @staticmethod
    def GetFuncPair( info):

        for item in tqdm(info):
            funca=item[0]
            funcb=item[1]
            pred=item[2]
            label=item[3]
            yield funca,funcb,pred,label


        # return y_true,y_pred
    @staticmethod
    def preprocess_slienceinfo(sliences):
        resul={}
        for slience_funcname,slience_info in sliences.items():
            # try:
            caller1,callee,index=slience_funcname.split("@@")
            if config.test_vul==True:
                if "FUN" in caller1:
                    caller1=str(int(caller1.replace("FUN_",""),16))
            if caller1 in resul:
                assert {(callee,index):slience_info} not in resul[caller1]
            else:
                resul[caller1]=[]
            resul[caller1].append({(callee, index): slience_info})
            # except Exception as e:
            #     print(e)
            #     print("解析slience_funcname出现错误：{}".format(slience_funcname))
        return resul

    def filter_num_param_fine(self,slience,slience1):
        return self.ComSlience_int_fine(slience,slience1,"num_param",config.number_threold)

    def filter_number_call_param_fine(self,slience,slience1):
        return self.ComSlience_int_fine(slience, slience1, "number_call_param", config.number_threold)

    def filter_number_var_fine(self,slience,slience1):
        return self.ComSlience_int_fine(slience, slience1, "number_var", config.number_threold)


    def filter_number_call_fine(self,slience,slience1):
        return self.ComSlience_int_fine(slience, slience1, "number_call", config.number_threold)

    def filter_number_const_fine(self,slience,slience1):
        return self.ComSlience_int_fine(slience, slience1, "number_const", config.number_threold)

    def filter_number_slienceLen_fine(self,slience,slience1):
        return self.ComSlience_int_fine(slience, slience1, "Slience_len", config.number_threold)

    @staticmethod
    def filter_varType(slience,slience1):
        all_arraylen = set()
        all_arraylen1 = set()
        for info in slience:
            for k, v in info.items():
                all_arraylen = all_arraylen | set(vd[list(vd)[0]] for vd in v["varMap"])

        for info in slience1:
            for k, v in info.items():
                all_arraylen1 = all_arraylen1 | set(vd[list(vd)[0]] for vd in v["varMap"])

        len_and = len(all_arraylen1 & all_arraylen)
        if abs(len_and - len(all_arraylen1)) == 0 or abs(len_and - len(all_arraylen)) ==0:
            return 1
        else:
            return 0

    def filter_varType_fine(self,slience,slience1):
        """
        细粒度检测常数，记录callee的每个常量列表，如果两个常量列表的交集为其中一个常量列表，则记录为true
        当所有callee中true满足一定比例，认为相似
        :param slience:
        :param slience1:
        :return:
        """
        # print("filter_constValue_fine")
        all_const=dict()
        all_const1 = dict()
        for info in slience:
            for k,v in info.items():
                if config.test_vul==True:
                    if (k[0].startswith("FUN_")):#FUN_0007d7ac
                        all_const[("FUN",k[1])]=v
                    else:
                        all_const[k] = v
                else:
                    all_const[k] = v

        for info in slience1:
            for k,v in info.items():
                if config.test_vul == True:
                    if (k[0].startswith("FUN_")):  # FUN_0007d7ac
                        all_const1[("FUN", k[1])] = v
                    else:
                        all_const1[k] = v
                else:
                    all_const1[k] = v

        result_flag=[]
        for callee_name,info in all_const.items():
            if callee_name in all_const1:
                callee_Array= [Adi[list(Adi)[0]] for Adi in  all_const[callee_name]["varMap"]]
                callee_Array1 = [Adi[list(Adi)[0]] for Adi in  all_const1[callee_name]["varMap"]]

                and_constinfo= set(callee_Array)&set(callee_Array1)
                if len(and_constinfo)==len(set(callee_Array)) or len(and_constinfo)==len(set(callee_Array1)):
                    result_flag.append(1)
                else:
                    result_flag.append(0)
            else:
                result_flag.append(0)
        # self.all_KeyStatment.append(len(result_flag)) #+= len(result_flag)
        if(result_flag.count(1)/len(result_flag))>=config.set_threold:
            return 1
        else:
            return 0

    @staticmethod
    def filter_constValue(slience,slience1):
        all_const=set()
        all_const1 = set()
        for info in slience:
            for k,v in info.items():
                all_const=all_const|set(v["const_list"])

        for info in slience1:
            for k,v in info.items():
                all_const1=all_const1|set(v["const_list"])

        len_and=len(all_const1&all_const)
        if abs(len_and-len(all_const1))<=2 or abs(len_and-len(all_const))<=2 :
            return 1
        else:
            return 0
        # if len(all_const1^all_const)==1:#严格对称差过滤
        #     return 1
        # else:
        #     return 0

    def filter_constValue_fine(self,slience,slience1):
        """
        细粒度检测常数，记录callee的每个常量列表，如果两个常量列表的交集为其中一个常量列表，则记录为true
        当所有callee中true满足一定比例，认为相似
        :param slience:
        :param slience1:
        :return:
        """
        # print("filter_constValue_fine")
        all_const=dict()
        all_const1 = dict()
        for info in slience:
            for k,v in info.items():
                if config.test_vul==True:
                    if (k[0].startswith("FUN_")):#FUN_0007d7ac
                        all_const[("FUN",k[1])]=v
                    else:
                        all_const[k] = v
                else:
                    all_const[k] = v

        for info in slience1:
            for k,v in info.items():
                if config.test_vul == True:
                    if (k[0].startswith("FUN_")):  # FUN_0007d7ac
                        all_const1[("FUN", k[1])] = v
                    else:
                        all_const1[k] = v
                else:
                    all_const1[k] = v
                # all_const1[k] = v

        result_flag=[]
        for callee_name,info in all_const.items():
            if callee_name in all_const1:
                callee_constinfo=all_const[callee_name]["const_list"]
                callee_constinfo1 = all_const1[callee_name]["const_list"]
                and_constinfo= set(callee_constinfo)&set(callee_constinfo1)
                if len(and_constinfo)==len(set(callee_constinfo)) or len(and_constinfo)==len(set(callee_constinfo1)):
                    result_flag.append(1)
                else:
                    result_flag.append(0)
            else:
                result_flag.append(0)
        # self.all_KeyStatment.append(len(result_flag)) #+= len(result_flag)
        if(result_flag.count(1)/len(result_flag))>=config.set_threold:
            return 1
        else:
            return 0


    def filter_arrayLen_fine(self,slience,slience1):
        """
        细粒度检测常数，记录callee的每个常量列表，如果两个常量列表的交集为其中一个常量列表，则记录为true
        当所有callee中true满足一定比例，认为相似
        :param slience:
        :param slience1:
        :return:
        """
        # print("filter_constValue_fine")
        all_const=dict()
        all_const1 = dict()
        for info in slience:
            for k,v in info.items():
                if config.test_vul==True:
                    if (k[0].startswith("FUN_")):#FUN_0007d7ac
                        all_const[("FUN",k[1])]=v
                    else:
                        all_const[k] = v
                else:
                    all_const[k] = v

        for info in slience1:
            for k,v in info.items():
                if config.test_vul == True:
                    if (k[0].startswith("FUN_")):  # FUN_0007d7ac
                        all_const1[("FUN", k[1])] = v
                    else:
                        all_const1[k] = v
                else:
                    all_const1[k] = v

        result_flag=[]
        for callee_name,info in all_const.items():
            if callee_name in all_const1:
                callee_Array= [Adi[list(Adi)[0]] for Adi in  all_const[callee_name]["ArrayMap"]]
                callee_Array1 = [Adi[list(Adi)[0]] for Adi in  all_const1[callee_name]["ArrayMap"]]

                and_constinfo= set(callee_Array)&set(callee_Array1)
                if len(and_constinfo)==len(set(callee_Array)) or len(and_constinfo)==len(set(callee_Array1)):
                    result_flag.append(1)
                else:
                    result_flag.append(0)
            else:
                result_flag.append(0)
        self.all_KeyStatment.append(len(result_flag)) #+= len(result_flag)
        if(result_flag.count(1)/len(result_flag))>=config.set_threold:
            return 1
        else:
            return 0
    @staticmethod
    def filter_arrayLen(slience,slience1):
        all_arraylen = set()
        all_arraylen1 = set()
        for info in slience:
            for k, v in info.items():
                all_arraylen = all_arraylen | set(vd[list(vd)[0]] for vd in v["ArrayMap"])

        for info in slience1:
            for k, v in info.items():
                all_arraylen1 = all_arraylen1 | set(vd[list(vd)[0]] for vd in v["ArrayMap"])

        len_and = len(all_arraylen1 & all_arraylen)
        if abs(len_and - len(all_arraylen1)) == 0 or abs(len_and - len(all_arraylen)) ==0:
            return 1
        else:
            return 0

    def filter_slience_info(self,funca,funcb,good_dataset=-1):
        """
        good_dataset为-1，过滤一个caller中不包含callee的情况，在这种情况下不收集该caller信息
        good_dataset为0则一个caller中不包含callee，认为比较结果为不相似，方法有较高的精确率，召回率较低
        good_dataset为1则一个caller中不包含callee，认为比较结果为相似，方法有较高召回率，但是精确率较低，
                        在漏洞检测场景中选1最好（只有过了相似性校验的caller才能执行这里）
        如，caller中关键key数量、callee数量
        good_dataset 为True则过滤数据集中不包含callee的
        :return: 返回值-1，不收集该caller的正误；返回值为1为预测结果为正；返回值为0表示预测结果为负
        """
        method_list=self.method_list
        def set_result_value(value):
            for i in method_list:
                result_dict[i]=value

        def yield_result():
            for key, v in result_dict.items():
                yield v, key

        result_dict = {}
        # assert
        if config.test_vul==True:
            try:
                funcname_a=str(int(funca["fun_name"], 16))
            except:
                funcname_a=funca["fun_name"]
            try:
                funcname_b=str(int(funcb["fun_name"], 16))
            except:
                funcname_b=funcb["fun_name"]
        else:
            funcname_a = funca["fun_name"]
            funcname_b = funcb["fun_name"]

        if funcname_a in self.SlenceInfo[funca["file_name"]] and \
            funcname_b in self.SlenceInfo[funcb["file_name"]]:
            slience_lista=self.SlenceInfo[funca["file_name"]][funcname_a]
            slience_listb=self.SlenceInfo[funcb["file_name"]][funcname_b]
        elif funcname_a in self.SlenceInfo[funca["file_name"]] or \
            funcname_b in self.SlenceInfo[funcb["file_name"]]:
            set_result_value(0)
            # yield_result()
            # for key, v in result_dict.items():
            #     yield v, key
            return result_dict
        else:
            set_result_value(good_dataset)
            # yield_result()
            # for key, v in result_dict.items():
            #     yield v, key
            return result_dict

        if abs(len(slience_lista)-len(slience_listb))==0:
            self.call_num_equal= True
        else:
            self.call_num_equal = False


        result_dict["filter_constValue_fine"]=self.filter_constValue_fine(slience_lista, slience_listb)
        result_dict["filter_arrayLen_fine"] = self.filter_arrayLen_fine(slience_lista, slience_listb)
        result_dict["filter_varType_fine"] = self.filter_varType_fine(slience_lista, slience_listb)

        result_dict["filter_number_slienceLen_fine"] = self.filter_number_slienceLen_fine(slience_lista, slience_listb)
        result_dict["filter_number_const_fine"] = self.filter_number_const_fine(slience_lista, slience_listb)
        result_dict["filter_number_call_fine"] = self.filter_number_call_fine(slience_lista, slience_listb)
        result_dict["filter_number_var_fine"] = self.filter_number_var_fine(slience_lista, slience_listb)
        result_dict["filter_number_call_param_fine"] = self.filter_number_call_param_fine(slience_lista, slience_listb)
        result_dict["filter_num_param_fine"] = self.filter_num_param_fine(slience_lista, slience_listb)
        # result_dict["preprocess_slienceinfo"] = self.preprocess_slienceinfo(slience_lista, slience_listb)
        # result_dict["filter_number_call_fine"] = self.filter_number_call_fine(slience_lista, slience_listb)
        # result_dict["filter_number_call_fine"] = self.filter_number_call_fine(slience_lista, slience_listb)
        # for key, v in result_dict.items():
        #     yield v, key
        return result_dict
        # return result_dict
        # return self.filter_number_slienceLen(slience_lista,slience_listb)

        # if self.filter_arrayLen_fine(slience_lista, slience_listb)==1 and \
        #         self.filter_constValue_fine(slience_lista,slience_listb)==1:
        #     return 1
        # else:
        #     return 0

        # return self.filter_arrayLen_fine(slience_lista, slience_listb)



        # return self.filter_arrayLen(slience_lista, slience_listb)
        # return self.filter_varType(slience_lista, slience_listb)


if __name__=="__main__":
    filter=Filter()
    # filter.get_slienceinfo()




