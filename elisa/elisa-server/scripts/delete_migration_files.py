import os
import shutil

apps = ['\\fei\\migrations', '\\school\\migrations', '\\timetables\\migrations', '\\requirements\\migrations']
cur_dir = os.getcwd().replace('\\scripts', '')
for app_name in apps:
    dir_path = cur_dir + app_name
    shutil.rmtree(dir_path)
    print(f'Removed migration folder for -> {app_name}')
