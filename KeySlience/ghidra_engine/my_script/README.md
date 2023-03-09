# CallParamSlience

## 简介

使用ghidra获取伪代码

根据伪代码跨函数追踪关键变量（目前不能跟进调用，只能跳出函数）


得到信息如下
- 关键变量对应的pcode
- 关键变量对应的伪代码指令
- 关键变量切片的统计信息

## 运行
java版本：java version "17.0.5" 2022-10-18 LTS
ghidra版本：ghidra_10.1.4_PUBLIC



- 为ghidra安装外部依赖：拷贝lib中文件到ghidra_10.1.4_PUBLIC/Ghidra/Features/Base/lib
- 执行：
```bash
runPath="./"  #在 my_script 目录下运行
analyzeHeadless $runPath/out/project aa -scriptPath $runPath/src -postScript Comfu_function.java \
-import $runPath/out/binary -overwrite


#aa为项目名
#out/project 为存放项目的目录
#out/binary  为要分析的二进制文件所在的路径（文件名或目录名）
```
调试参考
https://blog.csdn.net/weixin_49393427/article/details/122074023
直接在安装插件的时候搜索ghidra，不用手动编译插件

## 问题
从反编译结果追踪问题：
- 一个变量可能在多条指令被赋值，可能多条赋值都有用，目前的策略为追踪所有的赋值。在pcode层面由于SSA树形不存在该问题。