runPath="/home/yuqing/Desktop/10t-net/tower/PaperProject/SimFilter/KeySlience/ghidra_engine/my_script/"  #在 my_script 目录下运行
dataPath="/home/yuqing/Desktop/10t-net/tower/PaperProject/SimFilter/data/GhidraSlience/Vul/binary/"
projectPath="/home/yuqing/Desktop/10t-net/tower/PaperProject/SimFilter/data/GhidraSlience/Vul/project"
analyzeHeadless $projectPath aa -scriptPath $runPath/src -postScript Comfu_function.java \
-import $dataPath -overwrite
