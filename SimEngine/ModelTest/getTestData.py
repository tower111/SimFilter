import os
import argparse
import site
from tqdm import  tqdm
import cachetools
import pandas as pd
import json
import random
import ujson
from functools import lru_cache
import time
from itertools import combinations

class Vul():

    def __init__(self,xlsx_path):
        self.xlsx_path=xlsx_path
        self.name=self.excel_one_line_to_list(0)[2:]
        self.vul_id = self.excel_one_line_to_list(4)[2:]
        self.crash_address=self.excel_one_line_to_list(8)[2:]
        self.binary_md5=self.excel_one_line_to_list(9)[2:]
        self.function_addr = self.excel_one_line_to_list(10)[2:]
        self.block_addr = self.excel_one_line_to_list(14)[2:]

        self.dict_info={}
        for name,vul,clash,md5,func,block in zip(self.name,self.vul_id,self.crash_address,self.binary_md5
                ,self.function_addr,self.block_addr):
            key=md5.strip().lower()
            self.dict_info[key]=(name,vul,clash,func,block)


    def excel_one_line_to_list(self,item):
        df = pd.read_excel(self.xlsx_path, usecols=[item],
                           names=None)  # 读取项目名称列,不要列名
        df_li = df.values.tolist()
        result = []
        for s_li in df_li:
            result.append(s_li[0])
        # print(result)
        return result

class getTestDataset(object):
    def __init__(self,FLAG):
        self.inputdir = FLAG.input
        self.vuldir = FLAG.vul
        self.datacenterdir = FLAG.datacenter
        self.truepairs = None
        self.falsepairs = None
        self.file_list = self.scan_for_file(self.inputdir)
        self.vul_list= self.getvul(self.vuldir)
        self.min_node = int(FLAG.min_node)
        self.max_node = int(FLAG.max_node)


    def getvul(self,vuldir):
        file_list=self.scan_for_file(vuldir)
        self.vul=Vul(self.vuldir+"/result.xlsx")
        result=[]
        founded_binary=[]
        for filename in file_list:
            vul_md5=os.path.basename(filename).lower().strip().replace(".json","")
            if vul_md5 in self.vul.dict_info:
                founded_binary.append(vul_md5)
                with open(filename,"r") as fd:
                    content=json.loads(fd.read())
                for func in content["functions"]:
                    if int(func["address"],16)==int(self.vul.dict_info[vul_md5][3],16):
                        func["md5"]=vul_md5
                        func["vul_name"]=self.vul.dict_info[vul_md5][0]
                        func["vul_id"]=self.vul.dict_info[vul_md5][1]
                        func["crash_addr"]=self.vul.dict_info[vul_md5][2]
                        func["vul_func"] = self.vul.dict_info[vul_md5][3]
                        func["vul_block"] = self.vul.dict_info[vul_md5][4]
                        result.append(func)
                        break
                else:
                    print("vul not found :",vul_md5)
                # result[vul_md5]=(self.vul.dict_info[vul_md5],content)

        return result



    def scan_for_file(self,start):
        file_list = []
        for root, dirs, files in os.walk(start):
            for file in files:
                file_list.append(os.path.join(start, file))
        print('Found ' + str(len(file_list)) + ' object files')
        random.shuffle(file_list)
        return  file_list
    @lru_cache(maxsize=None)
    def openfile(self,file_b):
        with open(file_b, 'r') as bfile:
            file_b_json = json.load(bfile)
        return file_b_json
    def get_sim_pairs(self,index_vul,funca, num,file_b):
        # pairs = list()
        # softb = os.path.basename(file_b)

        # file_b_json = self.openfile(file_b)
        # b_functions = file_b_json['functions']
        # for funb in file_b:
        false_pair = dict()
        if file_b['filename'] != 'UNKname':
            false_pair["funca"]=index_vul
            false_pair["funcb"]=num


                # false_pair['cfga'] = funca['blocks']
                # false_pair['cfgb'] = funb['blocks']
                # false_pair['softa'] = str(funca["md5"])
                # false_pair['softb'] = str(softb)
                # false_pair['namea'] = funca['name']
                # false_pair['nameb'] = funb['name']
                # false_pair['filea'] = str(funca["md5"])
                # false_pair['fileb'] = file_b_json['filename']
                # # false_pair['addressa'] = funca['address']
                # # false_pair['addressb'] = funb['address']
                # # false_pair['similarity'] = '-1'
                # pairs.append(false_pair)
        return false_pair

    def get_dissim_pairs(self,file_a, file_b):
        pairs = list()
        softa =  os.path.basename(file_a)
        softb =  os.path.basename(file_b)
        with open(file_a, 'r') as afile:
            with open(file_b, 'r') as bfile:
                file_b_json = json.load(bfile)
                b_functions = file_b_json['functions']
                file_a_json = json.load(afile)
                a_functions = file_a_json['functions']
                for funa in a_functions:
                    a = random.choice(a_functions)
                    a_name = a['name']
                    cfga = a_name
                    for funb in b_functions:
                        b = random.choice(b_functions)
                        b_name = b['name']
                        cfgb = b_name
                        false_pair = dict()
                        if cfga != cfgb:
                            lena = len(funa['blocks'])
                            lenb = len(funb['blocks'])
                            if self.min_node<= lena <= self.max_node and self.min_node<= lenb <= self.max_node:
                                false_pair['cfga'] = a['blocks']
                                false_pair['cfgb'] = b['blocks']
                                false_pair['softa'] = str(softa)
                                false_pair['softb'] = str(softb)
                                false_pair['namea'] = a['name']
                                false_pair['nameb'] = b['name']
                                false_pair['addressa'] = a['address']
                                false_pair['addressb'] = b['address']
                                false_pair['similarity'] = '-1'
                                pairs.append(false_pair)
                                break
                            else:
                                pass
                        else:
                            pass

        return pairs

    def get_dataset(self):
        datacenterdir = self.datacenterdir
        # file_list = self.file_list
        # comp_files = list(combinations(file_list, 2))
        print(len(self.vul_list)*len(self.file_list))
        num = 0


        sim_pairs = list()
        dis_pairs = list()
        vul_index={}
        file_index={}
        for index,vul in enumerate(self.vul_list):
            vul_index[index]=vul
        filename=""
        num=0
        for index,dataset in enumerate(self.file_list):
            file_b_json = self.openfile(dataset)
            b_functions = file_b_json['functions']
            for funb in b_functions:
                funb["filename"]=file_b_json["filename"]
                file_index[num]=funb
                num+=1
            # filename=file_b_json["filename"]


        for index_vul,vul in enumerate(self.vul_list):
            # num=0

            for index_tested ,dataset in file_index.items():
            # for index_tested,dataset in enumerate(self.file_list):
                file_b = dataset
                t_pairs = self.get_sim_pairs(index_vul,vul,index_tested, file_b)
                sim_pairs.append(t_pairs)


        true_data = os.path.join(datacenterdir, "Testdataset.json")
        random.shuffle(sim_pairs)
        result={}
        result["vul"]=vul_index
        result["func"]=file_index
        result["pair"]=sim_pairs
        sjson=ujson.dumps(result)
        with open(true_data, 'w') as simfile:
            simfile.write(sjson)
            # json.dump(result, simfile, indent=4, ensure_ascii=False)
        print(true_data + ':' + 'done')




        self.truepairs = true_data

        self.creat_pairs()
        # self.dataset_statistic()

        return 0

    def get_dataset_statistic(self):
        datacenterdir = self.datacenterdir
        true_file = os.path.join(datacenterdir, "dataset.true.json")
        false_file = os.path.join(datacenterdir, "dataset.false.json")

        train_file = os.path.join(datacenterdir, "train_dataset.json")
        valid_file = os.path.join(datacenterdir, "valid_dataset.json")
        test_file = os.path.join(datacenterdir, "test_dataset.json")

        with open(true_file, 'r') as truefile:
            true_dataset = json.load(truefile)
            true_len = len(list(true_dataset))
            print(true_len)

        with open(false_file, 'r') as falsefile:
            false_dataset = json.load(falsefile)
            false_len = len(list(false_dataset))
            print(false_len)

        with open(train_file, 'r') as f:
            train_dataset = json.load(f)
            print(train_dataset['name'])
            t_set = train_dataset['data'][0]
            true_len = len(t_set)
            print(true_len)

        with open(valid_file, 'r') as f:
            valid_dataset = json.load(f)
            print(valid_dataset['name'])
            v_set = valid_dataset['data'][0]
            true_len = len(v_set)
            print(true_len)

        with open(test_file, 'r') as f:
            test_dataset = json.load(f)
            print(test_dataset['name'])
            t_set = test_dataset['data'][0]
            true_len = len(t_set)
            print(true_len)

    def creat_pairs(self):
        datacenterdir = self.datacenterdir
        random.seed(1234)

        testset = dict()

        testset['name'] = 'test dataset'

        true_file = os.path.join(datacenterdir, "dataset.true.json")
        false_file = os.path.join(datacenterdir, "dataset.false.json")

        test_file = os.path.join(datacenterdir, "test_dataset.json")

        with open(true_file, 'r') as truefile:
            with open(false_file, 'r') as falsefile:
                true_dataset = json.load(truefile)
                true_len = len(list(true_dataset))

                false_dataset = json.load(falsefile)
                false_len = len(list(false_dataset))

                print(true_len, false_len, false_len+true_len)



                testset['data'] = list()
                t_set = []
                t_set.extend(true_dataset[0:-1])
                t_set.extend(false_dataset[0:-1])
                random.shuffle(t_set)
                testset['data'].append(t_set)

                print(len(testset['data']))

                with open(test_file, 'w') as f:
                    json.dump(testset, f, indent=4, ensure_ascii=False)
                print(test_file + ':' + 'done')

        return 0

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", type=str, help="input ")
    parser.add_argument("-vul", "--vul", type=str, help="vul path ")
    parser.add_argument("-d", "--datacenter", type=str, help="output")
    parser.add_argument("-min", "--min_node", type=int, help="min_node")
    parser.add_argument("-max", "--max_node", type=int, help="max_node")
    args = parser.parse_args()


    pair_dataset = getTestDataset(args)
    # for test dataset
    pair_dataset.get_dataset()







