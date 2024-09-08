@echo off
call path\to\project\myvenv\Scripts\activate.bat
python path\to\project\services\TimeTrackerConsoleApp\main.py || pause
call path\to\project\myvenv\Scripts\deactivate.bat
