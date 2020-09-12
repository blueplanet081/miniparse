#!/usr/bin/env python3
'''
    ptree プロトタイプ版
    2020/08/21 by te.
'''
import sys
import pathlib
from typing import List
import miniparse2 as mp
import e2_path as e2


tMoji = 0                   # tree表記に使う文字種類  0: ASCII記号、1:拡張文字
dispFiles: bool = True
dispAll: bool = False
dispTreeLevel = 0


def show_directory(path: pathlib.Path, tlist: List[int] = []):
    ''' ディレクトリ以下の情報を再帰的に表示する。
        tlistは、ディレクトリ深度を表示するためのリスト
    '''
    tlevel = len(tlist)     # ツリーレベル

    dir_list = []           # そのディレクトリ内のサブディレクトリのリスト
    file_list = []          # そのディレクトリ内のファイルのリスト
    for po in path.iterdir():
        if not dispAll and (e2.is_HiddenName(po) or e2.is_SystemName(po)):
            continue
        if po.is_dir():         # ディレクトリのリストを作成
            dir_list.append(po)
        elif po.is_file():      # ファイルのリストを作成
            file_list.append(po)

    if (dispTreeLevel == 0 or tlevel < dispTreeLevel) and dir_list:
        dispDirs = True
    else:
        dispDirs = False


    # strHeader0  そのディレクトリを表示する、左側のヘッダー
    strHeader0 = ''
    for pre in tlist[0:-1]:
        strHeader0 += ['|   ', '│   '][tMoji] if pre else '    '

    # strHeader1  そのディレクトリ名を表示する、左側のヘッダー
    if tlevel == 0:             # 自分のディレクトリ名を表示（ツリーの先頭の場合）
        strHeader1 = ''
    elif tlist[-1] == 1:        # 自分のディレクトリ名を表示
        strHeader1 = strHeader0 + ['|-- ', '├── '][tMoji]
    else:                       # 自分のディレクトリ名を表示（最後のディレクトリの場合）
        strHeader1 = strHeader0 + ['+-- ', '└── '][tMoji]

    # strHeader2  そのディレクトリ内の情報を表示する、左側のヘッダー
    strHeader2 = strHeader0
    if tlevel != 0:
        strHeader2 += ['|   ', '│   '][tMoji] if tlist[-1] else '    '
    strHeader2 += ['|   ', '│   '][tMoji] if dispDirs else '   '

    print(strHeader1 + str(path))   # 自分のディレクトリ名を表示

    print(strHeader2 + f'dirs = {len(dir_list)}  files = {len(file_list)}')

    if dispFiles and file_list:
        print(strHeader2 + ' ',
              "ctime".ljust(17),
              "mtime".ljust(17),
              "length".rjust(8),
              "name"
              )
        for fn in file_list:            # ファイル名表示
            print(strHeader2 + ' ',
                  e2.get_dtctime(fn).strftime("%Y/%m/%d %H:%M "),
                  e2.get_dtmtime(fn).strftime("%Y/%m/%d %H:%M "),
                  f"{e2.get_fileSize(fn):>8,}",
                  fn.name)
    print(strHeader2)

    if dispDirs:              # ディレクトリあり→下位のディレクトリに潜る
        for po in dir_list[0:-1]:
            show_directory(po, tlist + [1])
        show_directory(dir_list[-1], tlist + [0])   # 最後のディレクトリ


''' ここからメイン ---------------------------- '''

# mp.partial_mode = mp.Pmode.WHOLE
# mp.usage_mode = mp.Umode.USAGE_AND_OPTION
# mp.error_code = 1

pm2: mp.TypeOpList = [('', False, '[ディレクトリ]'),
                      ('a', False, '', 'ドットやシステムディレクトリも表示'),
                      ('L', True, '階層数', '表示するディレクトリの深さを指定する'),
                      ('d', False, '', 'ディレクトリのみ表示'),
                      ('e', False, '', 'ツリーの表示に拡張文字を使用'),
                      ('h', False, '', '使い方を表示する'),
                      ('help', False, '', '使い方を表示する'),
                      ]
opp = mp.OpSet(pm2)
mp.miniparse(opp, sys.argv)

# ops = {'': mp.Oset(False, False, '[ディレクトリ]', ''),
#        'a': mp.Oset(False, False, '', 'ドットやシステムディレクトリも表示'),
#        'L': mp.Oset(False, True, '階層数', '表示するディレクトリの深さを指定する'),
#        'd': mp.Oset(False, False, '', 'ディレクトリのみ表示'),
#        'E': mp.Oset(False, False, '', 'ツリーの表示に拡張文字を使用'),
#        'h': mp.Oset(False, False, '', '使い方を表示'),
#        }

# myArgs = mp.wArgs(sys.argv)
# mp.miniparse(myArgs[1:], ops)

if opp.isTrue('h') or opp.isTrue('help'):
    print('ディレクトリやファイルのツリーを表示します。')
    print()
    mp.printUsage('', opp, mp.Umode.BOTH)

    sys.exit(0)

args = mp.get_arguments()
if args:
    path = pathlib.Path(args[0])
    if not path.is_dir():
        print(f'無効なディレクトリです {path}', file=sys.stderr)
        sys.exit(1)

else:
    path = pathlib.Path('.')

# dispFiles = True
# dispAll = False
dispTreeLevel = 0

if opp.isTrue('a'):
    dispAll = True
if opp.isTrue('d'):
    dispFiles = False
if opp.isTrue('e'):
    tMoji = 1

if opp.isTrue('L'):
    if opp.get_opArg('L')[0].isdecimal:
        dispTreeLevel = int(opp.get_opArg('L')[0])

show_directory(path.resolve())
