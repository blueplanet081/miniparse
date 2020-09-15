#!/usr/bin/env python3
# -------------------------------------------------------------
# miniparse 利用サンプル02
# ユーザ定義のエラーメッセージ上書き
# エラー時、ユーザ側で処理
# -------------------------------------------------------------

import sys
import miniparse as mp

mp.Eset['E0'] = "コマンドラインで、出力を開始するディレクトリを指定してください"
mp.Eset['E1'] = "そんなオプション（ {0} ）はありません"

pms: mp.TypeOpList = [('', True, 'ディレクトリ名'),
                      ('l', False, '', '詳細情報も表示する'),
                      ('h', False, '', '使い方を表示する'),
                      ('help', False, '', '使い方を表示する'),
                      ]


mp.error_mode = mp.Emode.SILENT_CONT

opp = mp.OpSet(pms)
mp.miniparse(opp, sys.argv)

err = mp.get_parseError()
if err:
    print('入力エラーです。')
    print(mp.make_errmsg(err))
    sys.exit(1)


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

