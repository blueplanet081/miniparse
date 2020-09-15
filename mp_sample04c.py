#!/usr/bin/env python3
# -------------------------------------------------------------
# miniparse 利用サンプル04c
# コマンドラインの解析をコマンド引数群で一旦停止しながら、
# その都度解析結果をリセットしながら、最後まで解析するサンプル
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
still_remain = mp.miniparse(opp, sys.argv)
''' miniparseの呼び出し、ここまで '''

while still_remain:
    ''' オプションの取得 '''
    mp.printOpset(opp)

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

    print()

    ''' オプション情報をリセットして、残りのコマンドラインの解析を続行 '''
    opp.reset_data()
    still_remain = mp.miniparse()

