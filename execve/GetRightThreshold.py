#coding=utf-8

import config
import json
from sklearn.metrics import accuracy_score,precision_score,recall_score
import matplotlib.pyplot as plt
from execve.utils.Filter import Filter
"""
通过相似性计算出合适的阈值
"""
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
    plt.xlabel("sim")
    plt.ylabel("acc")

    plt.savefig(config.trainResult+"/sim_acc.svg", format='svg')
    plt.show()


def get_sim_acc_png():
    """
    相似度为横坐标，准确率为纵坐标
    进一步改进：计算最大值

    :return:
    """
    info=getinfo(config.trainResult+"/compareResult.json")
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

    def show():
        print("method:{},acc:{},precision:{},recall:{}".format(method,round(acc,4),round(precision,4),round(recall,4)))
    filter=Filter()
    info=filter.Get_Sim()

    for index,(method,methodinfo)  in enumerate(info.items()):
        if index==0:
            print("文件总数：",len(filter.filename))
            print("样本总数：",len(methodinfo["realLable"]))
            print("正负样本数 正样本：负样本= ",methodinfo["realLable"].count(1.0),methodinfo["realLable"].count(-1.0))

        acc=accuracy_score(methodinfo["realLable"],methodinfo["predictLable"])
        precision=precision_score(methodinfo["realLable"],methodinfo["predictLable"])
        recall=recall_score(methodinfo["realLable"],methodinfo["predictLable"])
        show()
        # print("acc:",acc) #分类正确的样本占总样本个数的比例
        # print("precision: ",precision)#预测为正的样本中实际也为正的样本占被预测为正的样本的比例
        # print("recall: ",recall)#实际为正的样本中被预测为正的样本所占实际为正的样本的比例
if __name__=="__main__":

    # get_sim_acc_png()
    test_filter()