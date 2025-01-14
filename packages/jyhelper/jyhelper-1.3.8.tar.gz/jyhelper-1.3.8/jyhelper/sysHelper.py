#! /usr/bin/env python3
# -*- coding:utf-8 -*-
# @Time : 2025/01/13 18:35 
# @Author : JY
"""
系统相关的操作
"""

import subprocess
import sys


class sysHelper:

    @staticmethod
    def run_command(command, printInfo=True):
        """执行系统命令，实时显示输出，返回状态和结果"""
        lines = []
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True,
                                   universal_newlines=True)
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                outStr = output.strip()
                lines.append(outStr)
                if printInfo:
                    print(outStr)
                    sys.stdout.flush()
        # exit_code, lines
        return process.poll(), lines

    @staticmethod
    def red(msg):
        """print以后会显示红色字体"""
        return f"\033[31m{msg}\033[0m"

    @staticmethod
    def green(msg):
        """print以后会显示绿色字体"""
        return f"\033[32m{msg}\033[0m"

    @staticmethod
    def logError(msg1='', msg2='', msg3=''):
        """1个参数默认就是红色，2个或者3个参数msg2是红色"""
        if msg2 == '' and msg3 == '':
            print(sysHelper.red(msg1))
        elif msg2 != '' and msg3 == '':
            print(msg1, sysHelper.red(msg2))
        elif msg2 != '' and msg3 != '':
            print(msg1, sysHelper.red(msg2), msg3)

    @staticmethod
    def logInfo(msg1='', msg2='', msg3=''):
        if msg2 == '' and msg3 == '':
            print(sysHelper.green(msg1))
        elif msg2 != '' and msg3 == '':
            print(msg1, sysHelper.green(msg2))
        elif msg2 != '' and msg3 != '':
            print(msg1, sysHelper.green(msg2), msg3)


if __name__ == '__main__':
    sysHelper()
