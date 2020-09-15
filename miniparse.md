# miniparse -- 簡易コマンドラインパーサ（もう少し詳しい説明）

## オプション情報の定義


```py
import miniparse as mp

pm2: mp.TypeOpList = [('', False, 'ファイル名'),
                      ('l', False, '', '詳細情報も表示する'),
                      ('h', False, '', '使い方を表示する'),
                      ('help', False, '', '使い方を表示する'),
                      ]
opp = mp.OpSet(pm2)

```

  - １つのオプションにつき、ひとつの tuple　(str, bool, str, str)　のリストで定義する。
  - ひとつの tuple内の定義内容は以下のとおり</br>
  

      型      | 定義内容                                   | 省略時
      --------|-------------------------------------------|-------
      str     | オプション文字、または文字列                |
      bool    | そのオプションが引数をとるか（必須か）どうか | False（必須でない）
      str     | オプション引数の説明                       | 空文字列
      str     | オプションの説明                           | 空文字列
</br>

  - オプション引数の説明、オプションの説明は、自動生成する Usage:、またはオプションリストに使われる。この機能を使わない場合は、定義の必要は無い
  - オプション文字、または文字列の項が空文字列の場合は、「コマンド引数」の定義に使われる。
  その次の項目が Trueのとき、コマンドラインに「コマンド引数」の指定が無い場合はエラーになる。
  - 「コマンド引数」の定義の「オプション引数の説明」の項は、Usage:を自動生成する場合に、コマンド引数の説明として使われる。「オプションの説明」は無視される。</br>
  注）コマンド引数が省略可で、Usage: の自動生成での説明等が不要な場合、コマンド引数の定義そのものを省略できる。

</br>

### ユーザプログラムからの使用例
```py
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

```

### コマンドライン解析後の結果の取得方法
クラス OpSet のメソッドで取得

  - get_keys()  </br>
 　　オプション情報として定義された、オプション文字、文字列の一覧を返す。
  - isExist(op) </br>
 　　そのオプション文字、または文字列がオプション情報中に定義されているかどうか。
  - isTrue(op) </br>
   　　コマンドラインでそのオプション文字、または文字列（op）が指定されたら True。
  - isNeedArg(op) </br>
 　　そのオプションの引数が必須かどうか。
  - get_opArg(op) </br>
 　　コマンドラインで指定された、そのオプションの引数のリストを返す。</br>
 　　（繰り返し指定されると複数のオプション引数が存在するため、リストになっている）</br>
  - get_Argcomment(op) </br>
 　　オプション情報として定義された、そのオプションの引数の説明を取得する。
  - get_comment(op) </br>
 　　オプション情報として定義された、そのオプションの説明を取得する。
</br>
</br>

関数で取得

  - get_arguments() </br>
  　　コマンドラインで指定された、コマンド引数のリストを返す。
</br>
</br>
</br>

### オプション情報定義と、生成された Usage: の例
</br>

  - オプション情報定義の例</br>
  コマンド引数が省略可、オプション -L がオプション引数をとる（必須）

```py
pm2: mp.TypeOpList = [('', False, '[開始ディレクトリ]'),
                      ('a', False, '', 'ドットやシステムディレクトリも表示'),
                      ('L', True, '階層数', '表示するディレクトリの深さを指定する'),
                      ('d', False, '', 'ディレクトリのみ表示'),
                      ('e', False, '', 'ツリーの表示に拡張文字を使用'),
                      ('h', False, '', '使い方を表示する'),
                      ('help', False, '', '使い方を表示する'),
                      ]
opp = mp.OpSet(pm2)
```

  - 自動生成された Usage: とオプションリスト出力例
```
usage: ptree.py  -adeh -L階層数 --help    [開始ディレクトリ]
  -a: ドットやシステムディレクトリも表示
  -L 階層数:  表示するディレクトリの深さを指定する
  -d: ディレクトリのみ表示
  -e: ツリーの表示に拡張文字を使用
  -h: 使い方を表示する
  --help: 使い方を表示する
```
</br>
</br>

## エラー検出時の処理

### miniparseは、コマンドライン解析時に次のエラーを検出します。
- コマンド引数が必須の時、コマンド引数が入力されなかった</br>
　　エラーコード 'E0': "Command argument expected"
- 定義以外のオプションが入力された</br>
　　エラーコード 'E1': "Unknown option {0}"  （{0} にオプションが入る）
- オプション引数が必須のオプションが入力されたが、オプション引数が入力されなかった</br>
　　エラーコード 'E2': "Argument expected for the {0} option"  （{0} にオプションが入る）
</br>
</br>

### 上記エラーメッセージは、あらかじめユーザプログラム側で上書きすることができます。
使用例
```py
  import sys
  import miniparse2 as mp

  mp.Eset['E0'] = "コマンドラインで、出力を開始するディレクトリを指定してください"
  mp.Eset['E1'] = "そんなオプション（ {0} ）はありません"

  pm2: mp.TypeOpList = [('', True, 'ディレクトリ名'),
                        ('l', False, '', '詳細情報も表示する'),
                        ('h', False, '', '使い方を表示する'),
                        ('help', False, '', '使い方を表示する'),
                        ]
  opp = mp.OpSet(pm2)
  mp.miniparse(opp, sys.argv)

```


### エラー検出時の処理は、次の３通りになります。
- エラーメッセージを出力して処理終了（デフォルト）</br>
　　error_mode = Emode.ERROR_END　　　# 初期値
- エラーメッセージを出力して処理続行（ユーザプログラム側で終了処理を行う）</br>
　　error_mode = Emode.ERROR_CONT
- エラーメッセージを出力せずに処理続行（エラーメッセージ出力もユーザプログラム側で行う）</br>
　　error_mode = Emode.SILENT_CONT
</br>
</br>
</br>

エラー検出時の処理をユーザプログラム側で実行する例
```py
  mp.error_mode = mp.Emode.SILENT_CONT

  opp = mp.OpSet(pm2)
  mp.miniparse(opp, sys.argv)

  err = mp.get_parseError()
  if err:
      print('入力エラーです。')
      print(mp.make_errmsg(err))
      sys.exit(1)

```

実行例
```py
入力エラーです。
コマンドラインで、出力を開始するディレクトリを指定してください
```

### エラー処理に使用する関数

- get_parseError()</br>
  コマンドライン解析時のエラーを tuple型で取得する。エラーが無い時は空の tupleを返す。</br>
  tuple型のエラーの形式は、以下のとおり</br>
  　　　　(str:エラーコード, str:エラーの原因)　　ex) ('E1', '-L')

- make_errmsg(err)</br>
  定義済みのエラーメッセージ（原文）を元に、エラーメッセージ文字列を生成して返す。</br>
  　　err:　　get_parseError() で得られる tuple型のエラー</br>
  　　ex)　make_errmsg(('E1', '-L'))　で、文字列　"Unknown option -L" を返す

</br>
</br>
</br>

### miniparse 内でのエラーメッセージ出力処理
コマンドライン解析時にエラーが発生したとき、miniparse 内で出力するメッセージは以下になります。
1. make_errmsg() で生成されるエラーメッセージ
2. ユーザ登録のメッセージ（ユーザプログラム側で登録時）
3. 簡易的な Usage:（デフォルト）
4. オプションリスト（デフォルト）

エラー出力時に、2.～4. のメッセージを併せて出力するかどうかは、以下の定義によります。

```
  usage_mode = Umode.BOTH    # デフォルト

      Umode.NONE           # 出力しない
      Umode.USER           # ユーザ指定のメッセージを出力
      Umode.USAGE          # usage行のみ出力
      Umode.OLIST          # オプションリストを出力
      Umode.BOTH = Umode.USAGE | Umode.OLIST    # usage: とオプションリストの両方を出力
```
ユーザ指定のメッセージは、以下のように登録します。
```
  usage_usermessage = 'Usage:  plist -h | [-L<整数>] [-e] [ディレクトリ名]'
```
</br>
エラーメッセージと　Usage: をユーザ指定のものに付け替えた例

```py
    import sys
    import miniparse2 as mp

    mp.Eset['E0'] = "コマンドラインで、出力を開始するディレクトリを指定してください"
    mp.Eset['E1'] = "そんなオプション（ {0} ）はありません"

    pm2: mp.TypeOpList = [('', True, '開始ディレクトリ'),
                          ('L', True, '階層数', '表示するディレクトリの深さを指定する'),
                          ('e', False, '', 'ツリーの表示に拡張文字を使用'),
                          ('h', False, '', '使い方を表示する'),
                          ]


    mp.usage_mode = mp.Umode.USER | mp.Umode.OLIST
    mp.usage_usermessage = 'Usage:  plist.py  -h | [-L<整数>] [-e] [ディレクトリ名]'

    opp = mp.OpSet(pm2)
    mp.miniparse(opp, sys.argv)

```

エラー時の出力例
```
    そんなオプション（ -l ）はありません
    Usage:  plist.py  -h | [-L<整数>] [-e] [ディレクトリ名]
      -L 階層数:  表示するディレクトリの深さを指定する
      -e: ツリーの表示に拡張文字を使用
      -h: 使い方を表示する```
```
</br>
</br>

### エラー時のメッセージ出力先と、終了コード
miniparse 内で以下のように設定されています。どうしても言うなら、ユーザプログラム側で、miniparse() 呼び出し前に書き換えてください。
```py
    # エラー終了時のコード
    error_code = 1
    # エラーメッセージ出力先
    error_output: TextIO = sys.stderr

```


### printUsage() 関数
miniparse がエラー発生時に出力する Usage:関連のメッセージは、ユーザプログラムから利用することもできます。

  - printUsage(コマンド名, OpSetのインスタンス, Umode, 出力先)　</br>
  　　簡単な Usage:とかオプションリストなどを出力する。

    - コマンド名（省略時は、デフォルトのコマンド名）
    - OpSetのインスタンス（オプション情報を定義したもの）
    - Umode
      - Umode.USER　　 ユーザ定義のメッセージ
      - Umode.USAGE　　Usage行のみ出力する
      - Umode.OLIST　　オプションリストを出力する
      - Umode.BOTH　 　Usage: とオプションリストの両方を出力する
    - 出力先（sys.stdout とか、sys.stderr とか）
</br>
</br>
</br>

## 区切りモード
miniparse は、デフォルト状態ではコマンドラインを最後まで一度に解析します。そのため、コマンドライン上でコマンド引数が記述された後に入力されたオプションがあっても、先に記述されたオプションと同様に扱います。

>>コマンド名　<オプション群>　<コマンド引数群>　<オプション群２>　<コマンド引数群２> ...

</br>
各オプション群、コマンド引数群を個別に扱うには、区切りモードの指定を<全部モード>以外に設定します。

```
separation_mode: Smode = Smode.WHOLE   # デフォルト

    WHOLE = auto()      # 全部モード
    EVERY = auto()      # 個別モード
    ARG = auto()        # 引数区切りモード
    OPT = auto()        # オプション区切りモード
```

引数区切りモード（Smode.ARG）では、各<コマンド引数群>を解析後に、オプション区切りモード（Smode.OPT）では、各<オプション群>解析後に関数 miniparese() が一旦終了します。
個別モード（Smode.EVERY）では、各区切りごとに関数 miniparse() が一旦終了します。

後続の解析を続けるには、関数 miniparse() を引数なしで再度呼び出します。
後続の解析項目があるときは、関数 miniparse() の返り値が True、最後まで解析が終了した時は返り値が False になります。

後続の解析が必要ないときは、関数 miniparse() を再度呼び出す必要はありません。

未解析部分のコマンドラインは、関数 get_remainArgs() でリストとして取得できます。
</br>
</br>
</br>
</br>

### コマンドラインの解析を、最初のコマンド引数群で一旦停止するサンプル

```py
    #!/usr/bin/env python3
    # -------------------------------------------------------------
    # miniparse 利用サンプル04
    # コマンドラインの解析を、最初のコマンド引数群で一旦停止するサンプル
    # -------------------------------------------------------------

    import sys
    import miniparse2 as mp


    pm2: mp.TypeOpList = [('', False, '開始ディレクトリ'),
                          ('L', True, '階層数', '表示するディレクトリの深さを指定する'),
                          ('e', False, '', 'ツリーの表示に拡張文字を使用'),
                          ('h', False, '', '使い方を表示する'),
                          ('version', False, '', 'version情報を表示する'),
                          ]


    mp.separation_mode = mp.Smode.ARG           # コマンド引数区切りモード

    opp = mp.OpSet(pm2)
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

```
注）上記サンプルで ''' オプションの取得 ''' 部分の処理は、下記のデバッグ用関数を呼び出すことで同様の出力を得られます。
>>printOpset(OpSetのインスタンス)

</br>

### 出力例
```
mp_sample04.py -eL3 -h mp*.py -L -5 --ver *.md -L7 mi*.py

コマンド引数が入力された。 ['mp_sample04.py', 'mp_sample04b.py', 'mp_sample04c.py']
option -L が指定された。 オプション引数 = ['3']
option -e が指定された。
option -h が指定された。

コマンド引数リスト =
  'mp_sample04.py'
  'mp_sample04b.py'
  'mp_sample04c.py'

残りのコマンドラインリスト =
  '-L'
  '5'
  '--ver'
  'miniparse.md'
  'README.md'
  '-L7'
  'miniparse.py'
  'miniparse2.py'
  'miniparse_test2.py'
```



### コマンドラインの解析をコマンド引数群で一旦停止しながら、最後まで解析するサンプル
```py
#!/usr/bin/env python3
# -------------------------------------------------------------
# miniparse 利用サンプル04b
# コマンドラインの解析をコマンド引数群で一旦停止しながら、最後まで解析するサンプル
# -------------------------------------------------------------

import sys
import miniparse2 as mp


pm2: mp.TypeOpList = [('', False, '開始ディレクトリ'),
                      ('L', True, '階層数', '表示するディレクトリの深さを指定する'),
                      ('e', False, '', 'ツリーの表示に拡張文字を使用'),
                      ('h', False, '', '使い方を表示する'),
                      ('version', False, '', 'version情報を表示する'),
                      ]


mp.separation_mode = mp.Smode.ARG           # コマンド引数区切りモード

opp = mp.OpSet(pm2)
stillremain = mp.miniparse(opp, sys.argv)
''' miniparseの呼び出し、ここまで '''

while stillremain:
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

    ''' 残りのコマンドラインの解析を続行 '''
    stillremain = mp.miniparse()

```

### 出力例
```
mp_sample04.py -eL3 -h mp*.py -L -5 --ver *.md -L7 mi*.py

コマンド引数が入力された。 ['mp_sample04.py', 'mp_sample04b.py', 'mp_sample04c.py']
option -L が指定された。 オプション引数 = ['3']
option -e が指定された。
option -h が指定された。

コマンド引数リスト =
  'mp_sample04.py'
  'mp_sample04b.py'
  'mp_sample04c.py'

残りのコマンドラインリスト =
  '-L'
  '5'
  '--ver'
  'miniparse.md'
  'README.md'
  '-L7'
  'miniparse.py'
  'miniparse2.py'
  'miniparse_test2.py'

コマンド引数が入力された。 ['mp_sample04.py', 'mp_sample04b.py', 'mp_sample04c.py', 'miniparse.md', 'README.md']
option -L が指定された。 オプション引数 = ['3', '5']
option -e が指定された。
option -h が指定された。
option --version が指定された。

コマンド引数リスト =
  'mp_sample04.py'
  'mp_sample04b.py'
  'mp_sample04c.py'
  'miniparse.md'
  'README.md'

残りのコマンドラインリスト =
  '-L7'
  'miniparse.py'
  'miniparse2.py'
  'miniparse_test2.py'

コマンド引数が入力された。 ['mp_sample04.py', 'mp_sample04b.py', 'mp_sample04c.py', 'miniparse.md', 'README.md', 'miniparse.py', 'miniparse2.py', 'miniparse_test2.py']
option -L が指定された。 オプション引数 = ['3', '5', '7']
option -e が指定された。
option -h が指定された。
option --version が指定された。

コマンド引数リスト =
  'mp_sample04.py'
  'mp_sample04b.py'
  'mp_sample04c.py'
  'miniparse.md'
  'README.md'
  'miniparse.py'
  'miniparse2.py'
  'miniparse_test2.py'

残りのコマンドラインリスト =
```
</br>
</br>

### オプション情報をその都度リセットして、残りのコマンドラインの解析を続行する例
</br>
取得したオプション情報は、その都度付け足されていきます。解析の都度、オプション情報をリセットするには、reset_data() メソッドを使用します。

reset_data() メソッド使用例（部分）
```py
    ''' オプション情報をリセットして、残りのコマンドラインの解析を続行 '''
    opp.reset_data()
    still_remain = mp.miniparse()
```

### 出力例
```
mp_sample04.py -eL3 -h mp*.py -L -5 --ver *.md -L7 mi*.py

コマンド引数が入力された。 ['mp_sample04.py', 'mp_sample04b.py', 'mp_sample04c.py']
option -L が指定された。 オプション引数 = ['3']
option -e が指定された。
option -h が指定された。

コマンド引数リスト =
  'mp_sample04.py'
  'mp_sample04b.py'
  'mp_sample04c.py'

残りのコマンドラインリスト =
  '-L'
  '5'
  '--ver'
  'miniparse.md'
  'README.md'
  '-L7'
  'miniparse.py'
  'miniparse2.py'
  'miniparse_test2.py'

コマンド引数が入力された。 ['miniparse.md', 'README.md']
option -L が指定された。 オプション引数 = ['5']
option --version が指定された。

コマンド引数リスト =
  'mp_sample04.py'
  'mp_sample04b.py'
  'mp_sample04c.py'
  'miniparse.md'
  'README.md'

残りのコマンドラインリスト =
  '-L7'
  'miniparse.py'
  'miniparse2.py'
  'miniparse_test2.py'

コマンド引数が入力された。 ['miniparse.py', 'miniparse2.py', 'miniparse_test2.py']
option -L が指定された。 オプション引数 = ['7']

コマンド引数リスト =
  'mp_sample04.py'
  'mp_sample04b.py'
  'mp_sample04c.py'
  'miniparse.md'
  'README.md'
  'miniparse.py'
  'miniparse2.py'
  'miniparse_test2.py'

残りのコマンドラインリスト =

```
