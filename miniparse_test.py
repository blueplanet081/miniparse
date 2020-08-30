import sys
import miniparse as mp

mp.partial_mode = mp.Pmode.PARTIAL
mp.usage_mode = mp.Umode.USAGE_AND_OPTION
mp.error_code = 1

ops = {'': mp.Oset(False, False, 'ディレクトリ', ''),
       'a': mp.Oset(False, False, '', 'comment for a'),
       'L': mp.Oset(False, True, '階層数', 'Lのコメント'),
       'f': mp.Oset(False, False, '', 'これがfです'),
       'l': mp.Oset(False, False, '', 'これがlです'),
       'h': mp.Oset(False, False, '', '使い方を表示'),
       'verbose': mp.Oset(False, True, 'あれの長さ', '静かにね'),
       }

myArgs = mp.Args(sys.argv)
err = mp.miniparse(myArgs, ops)

if ops['h'].isTrue:
    print('このプログラムは、モジュール miniparse の使い方を示すものです。')
    mp.printUsage(myArgs.getCommandName(), ops, mp.Umode.USAGE_AND_OPTION)

print()
print('----')
mp.printOset(ops)

print('----')

if err:
    print('コマンドライン中にエラーがありました。')
    print(mp.Eset.Errmsg(err))

for p in ops:
    if len(p) == 1 and ops[p].isTrue:
        if ops[p].opArg:
            print(f'option -{p} {ops[p].opArg} が指定されました。')
        else:
            print(f'option -{p} が指定されました。')
    elif len(p) > 1 and ops[p].isTrue:
        if ops[p].opArg:
            print(f'option --{p}={ops[p].opArg} が指定されました。')
        else:
            print(f'option --{p} が指定されました。')

print()
print(f'コマンドラインアーギュメントとして、{mp.arguments()} が指定されました。')
print(f'残りのコマンドラインは {myArgs.getRemainArgs()} です。')
