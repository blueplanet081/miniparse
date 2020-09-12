#!/usr/bin/env python3
# -------------------------------------------------------------
# miniparse 利用サンプル01
# 一番シンプルなやつ
# -------------------------------------------------------------

import sys
import miniparse2 as mp

pm2: mp.TypeOpList = [('', False, 'ファイル名'),
                      ('l', False, '', '詳細情報も表示する'),
                      ('h', False, '', '使い方を表示する'),
                      ('help', False, '', '使い方を表示する'),
                      ]
opp = mp.OpSet(pm2)
mp.miniparse(opp, sys.argv)

''' miniparseの呼び出し、ここまで '''

''' オプションの取得 '''
for op in opp.get_keys():
    if opp.isTrue(op):
        if len(op) == 1:
            print(f'option -{op} が指定された。')
        if len(op) > 1:
            print(f'option --{op} が指定された。')

''' コマンド引数の取得 '''
arglist = mp.get_arguments()
if arglist:
    print()
    print('コマンド引数リスト = ')
    for arg in arglist:
        print(f'  [{arg}]')

print()

''' HELPメッセージ出力サンプル '''
if opp.isTrue('h') or opp.isTrue('help'):
    print('このプログラムは、モジュール miniparse の使い方を示すものです。')
    mp.printUsage('', opp, mp.Umode.BOTH)

