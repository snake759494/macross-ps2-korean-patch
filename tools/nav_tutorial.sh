#!/bin/sh
# boot -> main menu -> tutorial -> skip briefings -> mission
cd "/c/Users/Jay/Downloads/ps2/초시공요새마크로스"
sh tools/run.sh; sleep 28
python tools/emu.py key enter >/dev/null; sleep 5
python tools/emu.py key enter >/dev/null; sleep 4
python tools/emu.py key l >/dev/null; sleep 7
python tools/emu.py key down >/dev/null; sleep 1
python tools/emu.py key l >/dev/null; sleep 12
python tools/emu.py key i >/dev/null; sleep 10
python tools/emu.py key i >/dev/null; sleep 25
