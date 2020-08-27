# miniparse -- 簡易コマンドラインパーサ

作成経緯

CLIベースのコマンドを試作／製作するとき、起動オプションの処理を手軽に記述したかった。また、プログラムソース上からも見通しの良いものにしたかったため。

他に同種の手軽な手段を探したけれどまだ見つかりません。すでに同種の適当なものがあれば、教えていただければ幸いです。

</br>

## 使い方

```py
import sys
import miniparse as mp

ops = {'a': mp.Oset(False, False, 'comment for a'),
       'L': mp.Oset(False, True, 'Lのコメント'),
       'f': mp.Oset(False, False, 'これがfです'),
       'l': mp.Oset(False, False, 'これがlです'),
       'verbose': mp.Oset(False, True, '静かにね'),
       }

myArgs = mp.Args(sys.argv[1:])
```

コマンドラインオプションを定義する辞書型変数

key: １文字のオプション（頭にハイフンを付けて指定するもの）、または複数文字のオプション（頭にハイフンを２つ付けて指定するもの）