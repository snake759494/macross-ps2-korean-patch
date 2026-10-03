#!/bin/sh
# usage: tools/run.sh  -> boots Korean ISO in portable PCSX2
P="/c/Users/Jay/Downloads/ps2/초시공요새마크로스"
taskkill //IM pcsx2-qt.exe //F >/dev/null 2>&1; sleep 2
cd "$P/work/pcsx2" && (./pcsx2-qt.exe -fastboot -- "C:\Users\Jay\Downloads\ps2\초시공요새마크로스\Chou Jikuu Yousai Macross (Japan) (Korean).iso" >/dev/null 2>&1 &)
