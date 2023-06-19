import json
import os
from tqdm import tqdm

def onelen(path):
    with open(path) as fd:
        content=json.loads(fd.read())
    return len(content["functions"])

all=0
for i in tqdm(os.listdir("./data/binJson/")):
    all+=onelen("./data/binJson/"+i)
print(all)




# def onelen(path):
#     with open(path) as fd:
#         content=json.loads(fd.read())
#     return len(content)
#
# onelen("./data/datacenter/dataset.true.json")