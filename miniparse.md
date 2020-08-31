# miniparse -- 簡易コマンドラインパーサ

## 作成経緯

CLIベースのコマンドを試作／製作するとき、起動オプションの処理を手軽に記述したかった。同種のものを探したけど見つからなかったので、Python学習も兼ねて作成。

</br>

## パッケージ構成

ファイル名         | 内容
------------------|----
miniparse.md      | このドキュメント
miniparse.py      | miniparse本体（使うのに必要なのはこのファイルだけです）
ptree.py          | miniparse使用サンプル。いわゆる treeコマンドの試作版です。
e2_path.py        | ptree.pyが呼び出している自作ライブラリ（添付用簡易版）
miniparse_test.py | 古いテスト用プログラムです。見なかったことにしてください。

</br>


## 使い方

```py
import sys
import miniparse as mp

ops = {'': mp.Oset(False, False, '[ディレクトリ]', ''),
       'a': mp.Oset(False, False, '', 'ドットやシステムディレクトリも表示'),
       'L': mp.Oset(False, True, '階層数', '表示するディレクトリの深さを指定する'),
       'd': mp.Oset(False, False, '', 'ディレクトリのみ表示'),
       'E': mp.Oset(False, False, '', 'ツリーの表示に拡張文字を使用'),
       'h': mp.Oset(False, False, '', '使い方を表示'),
       }


```

１．辞書型の変数に、コマンドラインオプション情報を定義します。
* keyは、空文字はコマンドラインアーギュメント、１文字は - で指定するオプション、複数文字は -- で指定する長いオプションになります。
* クラス Oset の第一引数は、オプションが指定されたかどうかで、初期値は Falseを指定します。
* 第二引数は、オプションがアーギュメントをとるかどうかで、Trule/Falseを指定します。
* 第三引数、第四引数はコメントで、それぞれオプションアーギュメント、オプションの説明を書きます。</br>
  このコメントは、usage:メッセージを自動作成するときに使われます。

２．コマンドライン引数とコマンドラインオプション情報を指定して、miniparse() を呼びます。

```py
myArgs = mp.Args(sys.argv)
mp.miniparse(myArgs, ops)

```

３．結果は、以下のように取得します。
* 入力されたオプションは、ops['オプション'].isTrue が True になります。
* 入力されたオプションアーギュメントは、ops['オプション'].opArg に格納されます。
* コマンドアーギュメントは、mp.arguments() で取得します。List[str]型になります。
* コマンドラインオプション情報で、空文字のkeyを指定していた場合は、ops[''].opArg にも、コマンドアーギュメントが格納されます。（複数入力された場合は、最初の一つだけ）
</br></br>

以下使用例
```py
if ops['h'].isTrue:
    print('ディレクトリやファイルのツリーを表示します。')
    print()
    mp.printUsage(myArgs.getCommandName(), ops, mp.Umode.USAGE_AND_OPTION)

    sys.exit(0)

args = mp.arguments()
if args:
    path = pathlib.Path(args[0])
    if not path.is_dir():
        print(f'無効なディレクトリです {path}', file=sys.stderr)
        sys.exit(1)

else:
    path = pathlib.Path('.')

dispTreeLevel = 0

if ops['a'].isTrue:
    dispAll = True
if ops['d'].isTrue:
    dispFiles = False
if ops['E'].isTrue:
    tMoji = 1

if ops['L'].isTrue:
    if ops['L'].opArg.isdecimal:
        dispTreeLevel = int(ops['L'].opArg)

```