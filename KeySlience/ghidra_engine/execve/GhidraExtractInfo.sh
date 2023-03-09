runPath="./"  #在 my_script 目录下运行
analyzeHeadless $runPath/out/project aa -scriptPath $runPath/src -postScript Comfu_function.java \
-import $runPath/out/binary -overwrite