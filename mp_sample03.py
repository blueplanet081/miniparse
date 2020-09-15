#!/usr/bin/env python3
# -------------------------------------------------------------
# miniparse 利用サンプル03
# Usage:情報、ユーザ定義
# -------------------------------------------------------------

import sys
import miniparse as mp

mp.Eset['E0'] = "コマンドラインで、出力を開始するディレクトリを指定してください"
mp.Eset['E1'] = "そんなオプション（ {0} ）はありません"

pms: mp.TypeOpList = [('', True, '開始ディレクトリ'),
                      ('L', True, '階層数', '表示するディレクトリの深さを指定する'),
                      ('e', False, '', 'ツリーの表示に拡張文字を使用'),
                      ('h', False, '', '使い方を表示する'),
                      ]


mp.usage_mode = mp.Umode.USER | mp.Umode.OLIST
mp.usage_usermessage = 'Usage:  plist.py  -h | [-L<整数>] [-e] [ディレクトリ名]'

opp = mp.OpSet(pms)
mp.miniparse(opp, sys.argv)


''' miniparseの呼び出し、ここまで '''

''' オプションの取得 '''
for op in opp.get_keys():
    if opp.isTrue(op):
        if len(op) == 0 and opp.get_opArg(op):
            print('コマンド引数が入力された。', opp.get_opArg(op))
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

