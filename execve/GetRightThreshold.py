#coding=utf-8
import numpy as np

import config
import json
from sklearn.metrics import accuracy_score,precision_score,recall_score
import matplotlib.pyplot as plt
from execve.utils.Filter import Filter
"""
通过相似性计算出合适的阈值
"""
global_score_result={}
def getinfo(filename):
    with open(filename,"r")as fd:
        content=json.loads(fd.read())
    return content
def getaccuracy(sim,info):
    y_true=info["realLable"]
    y_pred=[]
    for pred in info["predictLable"]:
        if pred>sim:
            y_pred.append(1)
        else:
            y_pred.append(-1)
    return accuracy_score(y_true,y_pred)


def show(x,y):
    plt.plot(x, y, label="acc,sim")
    plt.xlabel("ST")
    plt.ylabel("Acc")

    plt.savefig(config.trainResult+"/sim_acc.png", format='png', dpi=500)
    plt.show()


def get_sim_acc_png():
    """
    相似度为横坐标，准确率为纵坐标
    进一步改进：计算最大值

    :return:
    """
    info=getinfo(config.trainResult+"/compareResult_testset.json")
    accs=[]
    sims=[]
    result={}
    for i in range(-100,100,1):
        sim=i/100.0
        acc=getaccuracy(sim,info)
        accs.append(acc)
        sims.append(sim)
        result[sim]=acc
    show(sims,accs)
    print(sorted(result.items(),key=lambda kv:(kv[1],kv[0]),reverse=True))

def test_filter():
    """
    测试经过过滤之后的准确率
    :return:
    """

    global_score_result[config.set_threold]=[]

    def show():
        print("method:{},acc:{},precision:{},recall:{}".format(method,round(acc,config.point_number),round(precision,config.point_number),round(recall,config.point_number)))
    def weigh_score():
        for info in methodinfo["predictLable"]:
            pass
    filter=Filter()
    info,file_info_right=filter.Get_Sim()


    weight_score_pred=np.mat(list([0.0]*len(info["rawMethod"]["realLable"])))
    weight_score_label=[]

    weight_score_matrix=[]
    mathod_list=[]
    print("ST: ",config.sim)
    print("PT: ",config.set_threold,config.number_threold)
    for index,(method,methodinfo)  in enumerate(info.items()):
        if index==0:
            # print("总样本数，总KeyStatement数，平均每个函数KeyStatement数量",len(methodinfo["realLable"]),filter.all_KeyStatment, filter.all_KeyStatment/len(methodinfo["realLable"]))
            print("KeyStatement数量中位数，众数，平均数：",np.median(filter.all_KeyStatment),
                  np.argmax(np.bincount(filter.all_KeyStatment)),np.mean(filter.all_KeyStatment))
            print("文件总数：",len(filter.filename))
            print("样本总数：",len(methodinfo["realLable"]))
            print("正负样本数 正样本：负样本= ",methodinfo["realLable"].count(1.0),methodinfo["realLable"].count(-1.0))
            weight_score_label=methodinfo["realLable"]

        print("预测正负样本数 正样本 ：负样本= ", methodinfo["predictLable"].count(1.0), methodinfo["predictLable"].count(-1.0))
        assert weight_score_label==methodinfo["realLable"]
        acc=accuracy_score(methodinfo["realLable"],methodinfo["predictLable"])
        precision=precision_score(methodinfo["realLable"],methodinfo["predictLable"])
        recall=recall_score(methodinfo["realLable"],methodinfo["predictLable"])
        show()
        global_score_result[config.set_threold].append((method,acc,precision,recall))
        mathod_list.append(method)

        # mt=np.mat(methodinfo["predictLable"])
        # weight_score_pred_tmp=filter.method_weight[method]*mt
        # weight_score_pred+=weight_score_pred_tmp

        weight_score_matrix.append(methodinfo["predictLable"])

    wmt=np.mat(weight_score_matrix)
    pred=[]
    attention_list=[mathod_list.index("filter_constValue_fine"),mathod_list.index('filter_arrayLen_fine'),mathod_list.index("filter_varType_fine")]

    for info in wmt.T:
        if -1 in info.tolist()[0]: #[info.tolist()[0][i] for i in attention_list]:
          pred.append(-1)
        else:

            pred.append(1)
    def fileinfo2str(file_info_right):
        result={}
        for k,v in file_info_right.items():
            result[k]=[json.dumps(i) for i in v]
        return result

    set_result=fileinfo2str(file_info_right)
    finally_vul=set()
    for k,v in set_result.items():
        finally_vul=set(v)
        break
    for k, v in set_result.items():
        set_v=set(v)
        finally_vul=finally_vul & set_v
        # prev=set_v

    file_info_right["finally"]=[json.loads(i) for i in finally_vul]


    # pred=[]
    # aa=weight_score_pred.tolist()
    # for item in  aa[0]:
    #     if item >0.5:
    #         pred.append(1)
    #     else:
    #         pred.append(-1)
    acc=accuracy_score(weight_score_label,pred)
    precision=precision_score(weight_score_label,pred)
    recall=recall_score(weight_score_label,pred)
    print("预测正负样本数 正样本 ：负样本= ",pred.count(1),pred.count(-1))
    print("method:{},acc:{},precision:{},recall:{}".format("weight_score",round(acc,config.point_number),round(precision,config.point_number),round(recall,config.point_number)))
    global_score_result[config.set_threold].append(("weight_score",acc,precision,recall))
    global_score_result[config.set_threold].append(("SpecificVul",file_info_right))
    return global_score_result
        # weight_score_pred
        # print("acc:",acc) #分类正确的样本占总样本个数的比例
        # print("precision: ",precision)#预测为正的样本中实际也为正的样本占被预测为正的样本的比例
        # print("recall: ",recall)#实际为正的样本中被预测为正的样本所占实际为正的样本的比例
import matplotlib.pyplot as plt
def showplt(x,y,method,co,ylable):

    plt.plot(x, y, 's-', markersize=1,color=co,label=method)  # s-:方形
    # plt.plot(x, k2, 'o-', color='g', label="CNN-RLSTM")  # o-:圆形
    plt.xlabel("PT")  # 横坐标名字
    plt.ylabel(ylable)  # 纵坐标名字
    plt.legend()
    # plt.show()

if __name__=="__main__":

    # get_sim_acc_png()
    test_filter()

    def get_TP_png():
        for item in range(0,10,1):
            threold=item/10
            config.set_threold=threold
            config.number_threold=threold
            result=test_filter()

        with open("./data/trainResult/Threshould.json","w") as fd:
            fd.write(json.dumps(global_score_result))
        with open("./data/trainResult/Threshould.json","r") as fd:
            global_score_result=json.loads(fd.read())

        line=[]
        constValue=[]
        ArrayLen=[]
        VarType=[]
        KSSLen=[]
        NumberConst=[]
        NumberCall=[]
        NumberVar=[]
        NumberCallerParam=[]
        NumberCalleeParam=[]
        raw=[]
        all=[]
        show_info_flag=1  #指定为1,2,3分别绘制3个指标的图案
        ylable=""
        if show_info_flag==1:
            ylable="Acc"
        elif show_info_flag==2:
            ylable="Precision"
        elif show_info_flag==3:
            ylable="Recall"
        else:
            assert 1==2
        for threold,info  in global_score_result.items():
            line.append(float(threold))
            constValue.append(info[0][show_info_flag])
            ArrayLen.append(info[1][show_info_flag])
            VarType.append(info[2][show_info_flag])
            KSSLen.append(info[3][show_info_flag])
            NumberConst.append(info[4][show_info_flag])
            NumberCall.append(info[5][show_info_flag])
            NumberVar.append(info[6][show_info_flag])
            NumberCallerParam.append(info[7][show_info_flag])
            NumberCalleeParam.append(info[8][show_info_flag])
            raw.append(info[9][show_info_flag])
            all.append(info[10][show_info_flag])
            assert info[0][0]=="filter_constValue_fine"

        fig = plt.figure()  # 创建画板
        showplt(line,constValue,"ConstValue","black",ylable)
        showplt(line, ArrayLen, "ArrayLen","teal",ylable)
        showplt(line, VarType, "VarType", "peru",ylable)
        showplt(line, KSSLen, "KSSLen", "darkorange",ylable)
        showplt(line, NumberConst, "NumberConst", "gold",ylable)
        showplt(line, NumberCall, "NumberCall", "lawngreen",ylable)
        showplt(line, NumberVar, "NumberVar", "green",ylable)
        showplt(line, NumberCallerParam, "NumberCallerParam", "deepskyblue",ylable)
        showplt(line, NumberCalleeParam, "NumberCalleeParam", "pink",ylable)
        showplt(line, raw, "Raw", "indigo", ylable)
        showplt(line, all, "finally", "crimson",ylable)
        fig.savefig("./data/trainResult/Threshould{}.png".format(show_info_flag), format='png', dpi=500)  # 输出
        plt.show()


    get_TP_png()
