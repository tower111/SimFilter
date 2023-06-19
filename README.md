



- exec为启动程序
- KeySlience为通过ghidra抽取数据的核心引擎
- SimEngine为相似性比较的引擎
- config.py为一些全局配置
- data存放数据
- 

## 用KeySlience抽取二进制文件信息

ProcessBinary.py 从之前的数据集中获取文件

KeySlience/ghidra_engine/execve/GhidraExtractInfo.sh 为启动抽取命令

## 训练二进制相似模型

参考SimEngine的readme



## 启动比较

execve/GetRightThreshold.py  计算出各项分值