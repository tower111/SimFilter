import os
import ujson
import config

os.environ['CUDA_VISIBLE_DEVICES']='0,1'
import torch.backends.cudnn as cudnn
import argparse
import torch
from torch import nn
from sklearn.metrics import accuracy_score
import random
import time
import json

import numpy as np



from getSearchBase import pairsDataset

# from BinaryEmbedding.Model.seqLSTMAttentionNetwork import seqLSTMAttentionNetwork
#
# from BinaryEmbedding.Model.seqGRU import seqGRUNetwork
#
# from BinaryEmbedding.Model.graphLSTMNetwork import graphLSTMNetwork
#
# from BinaryEmbedding.Model.GraphTransformerWithKB import  graphLSTMCatNetwork
# from BinaryEmbedding.Model.acfgGraphNetwork import  acfgGraphNetwork
# from BinaryEmbedding.Model.acfgSeqNetwork import acfgSeqLSTMAttentionNetwork



USE_CUDA = torch.cuda.is_available()

cudnn.benchmark = True

random.seed(1234)
np.random.seed(1234)
torch.manual_seed(1234)

"""
保存相似性比较的向量
"""

if USE_CUDA:
    DEVICE = torch.device('cuda' )
    print('***************')
    print('-----cuda------')
    print('***************')
    torch.cuda.manual_seed(1234)
else:
    DEVICE = torch.device('cpu')


class x2vTrainer(object):
    def __init__(self, flags):
        self.network = flags.network
        self.best_network_model = flags.model
        self.datacenter = flags.datacenter

        self.batch_size = 50


        self.epochs = 10

        self.max_instructions = 50
        self.max_nodes = 150

        # seq
        self.seq_len = 150
        # kb seq length for all basic block with cat( func= graph + kb)
        self.kb_seq = 150
        # graph for node kb length
        self.node_kb_max = 5

        # path
        self.max_path = 2
        self.path_len = 30

        # self.lstm_batch_size = self.batch_size * self.max_nodes
        self.lr = 0.001

        # i2v
        self.embedding_dim = 100
        self.hidden_dim = 100

        self.output_dim = 64
        self.num_layers = 1

        self.n_heads = 4

        # acfg
        # self.acfg_length = 8
        self.acfg_length = 7


        self.get_data = pairsDataset(flags.word2id, flags.api2id,flags.search_dataset,self.seq_len,
                                          self.max_instructions,
                                          self.max_nodes,
                                          self.kb_seq,
                                          self.node_kb_max,
                                          self.max_path,
                                          self.path_len,
                                     config.test_vul
                                          )

        self.id2vec = self.matrix_load(flags.id2vec)
        # self.api2vec = self.matrix_load(flags.api2vec)
        # self.train_dataset = self.get_train_data.dataset
        # self.valid_dataset = self.get_valid_data.dataset
        self.test_dataset = self.get_data.dataset
        self.word2id = self.get_data.word2id

        self.graph_iteration = 2
        self.node_iteration = 2
        self.graph_dim = 64




        self.train_loss = []
        self.valid_loss = []
        self.min_valid_loss = np.inf
        self.val_auc = np.inf
        self.BEST_VAL_AUC = 0
        self.BEST_TEST_AUC = 0

    def matrix_load(self, id2vec):
        matrix = np.load(id2vec)
        return matrix


    def build_search_dataset(self):
        # model_name = "./X2V_seq_kb.model"
        model_name = self.best_network_model
        # best_model=torch.load(model_name).get('epoch')
        # print(best_model)
        # exit(0)
        best_model = torch.load(model_name).get('model').cuda()
        best_model.eval()

        final_predict = []
        ground_truth = []
        search_funcs_vec = list()

        test_dataset = self.test_dataset
        dataset_len = len(test_dataset)
        iterations = int(dataset_len / self.batch_size)
        result_pred = []
        result_lable = []
        for itera in range(0, iterations):
            if self.network.startswith('seq'):
                inputs, lable ,funcs= self.get_seq_search_inputs(itera, test_dataset)


            predictions, F1_embedding, F2_embedding = best_model(inputs)



            g_truth = lable.cpu().detach().numpy()

            final_pred = predictions.cpu().detach().numpy()

            ground_truth.extend(g_truth.tolist())
            final_predict.extend(final_pred.tolist())

            pairs = zip(funcs, F1_embedding, F2_embedding,final_pred)

            for funa,funveca,funvecb,pred in pairs:
                a_function_vec = dict()
                b_function_vec=dict()
                # for firmware
                # a_function_vec['object_name'] = funa['object_name']
                # for quick_search by filtering
                if config.test_vul==True:
                    funa["similarity"]=1
                    funca_info=self.get_data.vul[str(funa['funca'])]
                    a_function_vec['fun_nodes'] = len(funca_info)
                    a_function_vec['file_name']= funca_info['md5']
                    a_function_vec['fun_name'] = funca_info['address']
                    a_function_vec['fun_address'] = funca_info['address']
                    a_function_vec['fun_vec'] = funveca.cpu().detach().numpy().tolist()

                    funcb_info = self.get_data.func[str(funa['funcb'])]
                    b_function_vec['fun_nodes'] = len(funcb_info)
                    b_function_vec['file_name'] = funcb_info['filename']
                    b_function_vec['fun_name'] = funcb_info['name']
                    b_function_vec['fun_address'] = funcb_info['address']
                    b_function_vec['fun_vec'] = funvecb.cpu().detach().numpy().tolist()
                    search_funcs_vec.append((a_function_vec, b_function_vec, float(pred), float(1)))
                else:
                    a_function_vec['fun_nodes'] = len(funa['cfga'])
                    a_function_vec['file_name']= funa['filea']
                    a_function_vec['fun_name'] = funa['namea']
                    a_function_vec['fun_address'] = funa['addressa']
                    a_function_vec['fun_vec'] = funveca.cpu().detach().numpy().tolist()

                    b_function_vec['fun_nodes'] = len(funa['cfgb'])
                    b_function_vec['file_name']= funa['fileb']
                    b_function_vec['fun_name'] = funa['nameb']
                    b_function_vec['fun_address'] = funa['addressb']
                    b_function_vec['fun_vec'] = funvecb.cpu().detach().numpy().tolist()
                    search_funcs_vec.append((a_function_vec,b_function_vec,float(pred),float(funa["similarity"])))
                    print(a_function_vec['fun_name']+'-->done')

                if pred<config.sim:
                    result_pred.append(-1)
                else:
                    result_pred.append(1)
                result_lable.append(float(funa["similarity"]))

            print("%d/%d done" %(itera,iterations))
        print("准确率:",accuracy_score(result_lable , result_pred))

        fun_database = config.func_vector_info
        random.shuffle(search_funcs_vec)
        if config.test_vul==True:

            with open(config.trainResult+"/compareResult.json","w") as fd:
                fd.write(json.dumps({"realLable":ground_truth,"predictLable":final_predict}))
            with open(fun_database, 'w') as basefile:
                tmp=ujson.dumps(search_funcs_vec)
                basefile.write(tmp)
        else:
            with open(config.trainResult+"/compareResult_testset.json","w") as fd:
                fd.write(json.dumps({"realLable":ground_truth,"predictLable":final_predict}))
            with open(fun_database, 'w') as basefile:
                tmp=ujson.dumps(search_funcs_vec)
                basefile.write(tmp)

            # json.dump(search_funcs_vec, basefile, indent=4, ensure_ascii=False)
        print(fun_database + ':' + 'done')

    def get_seq_search_inputs(self,itera,dataset):

        start = itera*self.batch_size
        end = (itera+1)*self.batch_size
        # print(start, end)
        funcs = dataset[start:end]
        # g1_matrix, g2_matrix, lable,g1_api,g2_api,g1_length,g2_length,g1_api_length,g2_api_length

        pair = self.get_data.get_seq_singles(funcs,funca=False)

        g1_inputs = torch.tensor(pair[0])

        g2_inputs = torch.tensor(pair[1])
        lable = torch.Tensor(pair[2]).to(DEVICE)
        g1_api = torch.tensor(pair[3])
        g2_api = torch.tensor(pair[4])
        g1_length = torch.tensor(pair[5])
        g2_length = torch.tensor(pair[6])
        g1_api_length = torch.tensor(pair[7])
        g2_api_length = torch.tensor(pair[8])



        inputs = [g1_inputs,g2_inputs,lable,g1_api,g2_api,g1_length,g2_length,g1_api_length,g2_api_length]

        return inputs,lable,funcs






if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--word2id", type=str, help="word2id to analyze")
    parser.add_argument("-v", "--id2vec", type=str, help="id2vec to analyze")
    parser.add_argument("-d", "--datacenter", type=str, help="datacenter for analyze")
    # parser.add_argument("-y", "--valid_dataset", type=str, help="train_dataset for analyze")
    parser.add_argument("-z", "--search_dataset", type=str, help="train_dataset for analyze")
    parser.add_argument("-n", "--network", type=str, help="network for analyze")
    parser.add_argument("-m", "--model", type=str, help="model network for test")

    parser.add_argument("-ai", "--api2id", type=str, help="word2id to analyze")
    parser.add_argument("-av", "--api2vec", type=str, help="id2vec to analyze")
    args = parser.parse_args()
    # args.network: Graph_Transformer\Graph_BiLSTM\seq_Attention_LSTM\seq_LSTM
    print(time.asctime(time.localtime(time.time())))

    trainer = x2vTrainer(args)

    trainer.build_search_dataset()

    print(time.asctime(time.localtime(time.time())))
