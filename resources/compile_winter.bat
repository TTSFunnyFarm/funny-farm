@echo off
echo Compiling winter.mf...
cd winter
..\..\..\cio-panda3d\built_x64\bin\multify -c -f ..\winter.mf winter phase_3.5 phase_4 phase_6
echo Done!
PAUSE