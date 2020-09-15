#!/usr/bin/env python3
# -------------------------------------------------------------
# miniparse 利用サンプル04
# コマンドラインの解析を、最初のコマンド引数群で一旦停止するサンプル
# -------------------------------------------------------------

import sys
import miniparse as mp


pms: mp.TypeOpList = [('', False, '開始ディレクトリ'),
                      ('L', True, '階層数', '表示するディレクトリの深さを指定する'),
                      ('e', False, '', 'ツリーの表示に拡張文字を使用'),
                      ('h', False, '', '使い方を表示する'),
                      ('version', False, '', 'version情報を表示する'),
                      ]


mp.separation_mode = mp.Smode.ARG           # コマンド引数区切りモード

opp = mp.OpSet(pms)
stillremain = mp.miniparse(opp, sys.argv)
''' miniparseの呼び出し、ここまで '''

''' オプションの取得 '''
# mp.printOpset(opp)
for op in opp.get_keys():
    if opp.isTrue(op):
        if len(op) == 0 and opp.get_opArg(op):
            print('コマンド引数が入力された。', opp.get_opArg(op))
        if len(op) == 1:
            print(f'option -{op} が指定された。',
                  f'オプション引数 = {opp.get_opArg(op)}' if opp.get_opArg(op) else '')
        if len(op) > 1:
            print(f'option --{op} が指定された。',
                  f'オプション引数 = {opp.get_opArg(op)}' if opp.get_opArg(op) else '')

''' コマンド引数の取得 '''
arglist = mp.get_arguments()
if arglist:
    print()
    print('コマンド引数リスト = ')
    for arg in arglist:
        print(f"  '{arg}'")

print()
remain_arglist = mp.get_remainArgs()
print('残りのコマンドラインリスト = ')
for arg in remain_arglist:
    print(f"  '{arg}'")

