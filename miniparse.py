from typing import Union, List, Dict, Tuple
import sys
import pathlib
'''
miniparse.py コマンドライン解析モジュール
version 0.5ぐらい
2020/8/27 by te.
'''

if sys.version_info < (3, 8):
    print('このモジュールは、Python 3.8以降に対応しています。ごめんなさい。')
    print('もし、モジュール内の <:=> 演算子部分を2行に書き換えれば、3.7以前でも動くかもしれません。')
    sys.exit()

# 全部モード or 個別モード
# 個別モードのときは、コマンドパラメータを検出した時に一旦終了する。
# 　--> command -axL param next --continue　の、param、next検出時など
WHOLE = 0       # 全部モード
PARTIAL = 1     # 個別モード
partial_mode = WHOLE

# エラーを検出したときにどうするか
ERROR_END = 0       # エラーを出力して終了
ERROR_CONT = 1      # エラーを出力して続行（miniparse() の戻り値がエラーID）
SILENT_CONT = 2     # エラーを出さずに続行（miniparse() の戻り値がエラーID）
error_mode = ERROR_END

# エラー終了時のコード
error_code = 1
# エラーメッセージ出力先
error_output = sys.stderr
# エラー時の追加メッセージ
error_message2 = ''


class Oset():
    def __init__(self, isTrue: bool = False, needParam: bool = False, comment: str = ''):
        ''' コマンドラインオプション情報を格納するclass
        '''
        self.isTrue = isTrue            # オプション状態(省略時は False)
        self.needParam = needParam      # オプションパラメータがあるか(省略時は False)
        self.param = ''                 # オプションパラメータ(初期値はナシ = 空白)
        self.comment = comment          # オプションの意味（任意）


def printOset(pm: Dict[str, 'Oset']) -> None:
    ''' コマンドラインオプション情報の一覧を表示する（デバッグ用）
    '''
    for pp in pm:
        print(pp, pm[pp].isTrue, pm[pp].param, pm[pp].comment)


class Eset():
    def __init__(self, emsg: str):
        ''' コマンドラインオプション情報を格納するclass
        '''
        self.emsg = emsg

    def __emsg(self, p0: str = '<p0>', p1: str = '<p1>') -> str:
        return self.emsg.format(p0, p1)

    @staticmethod
    def Errmsg(ueid: Union[str, Tuple[str, ...]], p0: str = 'p0', p1: str = 'p1') -> str:
        ''' クラス外で定義している辞書型の「Es」（エラーメッセージ原文）を用いて、
            エラーメッセージを生成する(static method)
        '''
        if type(ueid) is tuple:
            eid = ueid[0] if len(ueid) > 0 else 'XX'
            p0 = ueid[1] if len(ueid) > 1 else 'p0'
            p1 = ueid[2] if len(ueid) > 2 else 'p1'
        else:
            eid = ueid
        if eid in Es:
            return Eset.__emsg(Es[eid], p0, p1)
        else:
            return f"***Undefined message {eid}: <{p0}> <{p1}>"


Es = {'E0': Eset("Unkown option: -{0}"),
      'E1': Eset("Argument expected for the -{0} option"),
      'U0': Eset("Your message here {0} of {1}"),
      }


class Args():
    ''' コマンドライン解析用class
    '''
    def __init__(self, args: List[str]):
        ''' コマンドライン解析用インスタンスを作成
        '''
        self.__comName = args[0]    # コマンドパス名
        self.__args = args[1:]      # 解析用コマンドパラメータ
        self.__num = 0              # 解析中ブロックポインタ
        self.__pos = 0              # 解析中ブロック内ポインタ

    def getCommandPath(self) -> str:
        ''' コマンドパス名を返す
        '''
        return self.__comName

    def getCommandName(self) -> str:
        ''' コマンド名を返す
        '''
        p = pathlib.Path(self.__comName)
        return p.name

    def optionType(self) -> str:
        ''' オプションブロックのタイプを調べる
        '''
        if self.__args[self.__num].startswith('--'):
            self.__pos = 2
            return '--'         # ロングオプションブロック
        elif self.__args[self.__num].startswith('-'):
            self.__pos = 1
            return '-'          # ショートオプションブロック
        else:
            self.__pos = 0
            return ''           # パラメータブロック

    def getOne(self) -> str:
        ''' シングルオプションブロックから１文字取り出す
        '''
        tpos = self.__pos
        self.__pos += 1
        # print(tpos, self.__num)
        return self.__args[self.__num][tpos:tpos + 1]

    def getLong(self) -> str:
        ''' ロングオプションブロックから、オプションを取り出す
        '''
        tpos = self.__pos
        if (ppos := self.__args[self.__num][tpos:].find('=')) == -1:
            self.__pos = len(self.__args[self.__num])
            return self.__args[self.__num][tpos:]
        else:               # 後ろに '=xxx' のオプションパラメータあり
            self.__pos = tpos + ppos + 1
            return self.__args[self.__num][tpos:tpos + ppos]

    def getAll(self) -> str:
        ''' 引数ブロックの全体、または残りを取り出す
        '''
        lpos = self.__pos
        self.__pos = len(self.__args[self.__num])
        return self.__args[self.__num][lpos:]

    def transNext(self) -> bool:
        ''' 次の引数ブロックに移行する。
            途中でも強制的に次に移行するので注意。
            次が無かったらFalseを返す
        '''
        self.__num += 1
        self.__pos = 0
        return self.__num < len(self.__args)

    def isEndBlock(self) -> bool:
        ''' 現行ブロックの終わりならTrue。
            すべてのブロックが終了していてもTrue
        '''
        return self.isAllEnd() or self.__pos >= len(self.__args[self.__num])

    def isAllEnd(self) -> bool:
        ''' すべてのブロックが終了
        '''
        return self.__num >= len(self.__args)

    def getOpParam(self) -> str:
        ''' 次のブロックのオプションパラメータを取得する
        '''
        if self.transNext():
            if self.optionType() == '--' and self.isEndBlock():
                if self.transNext():
                    return self.getAll()
                else:
                    return ""
            elif self.optionType() == '':
                return self.getAll()
            # 次のブロックが無かったり、パラメータブロックだったら取得失敗
        return ""

    def remainArgs(self) -> List[str]:
        ''' 解析中のコマンドラインの残りを返す（解析位置等は更新されない）
        '''
        return self.__args[self.__num:]


__params = []
''' 取得したパラメータの格納用
'''


def params() -> List[str]:
    ''' 取得したパラメータのリストを返す
    '''
    return __params


def miniparse(tm: 'Args', pms: Dict[str, 'Oset']) -> Union[Tuple[()], Tuple[str, ...]]:
    ''' コマンドライン解析用モジュール
    '''
    err = ()
    while not tm.isAllEnd():
        if tm.optionType() == '-':      # シングルオプションブロック
            while p := tm.getOne():
                if p in pms:
                    pms[p].isTrue = True
                    if pms[p].needParam:    # オプションパラメータ必要
                        if op := tm.getAll():
                            pms[p].param = op
                        elif op := tm.getOpParam():
                            pms[p].param = op
                        else:
                            err = ('E1', p)  # E1: Argument expected for the -<p>
                        break
                else:
                    err = ('E0', p)     # E0: Unknown option: -<p>
                    tm.getAll()     # エラーなので、ブロックの残りを空読み
                    break

        elif tm.optionType() == '--' and (p := tm.getLong()):   # ロングオプションブロック
            if p in pms:
                pms[p].isTrue = True
                if op := tm.getAll():       # ブロックの後ろがまだあった -->'=xxxx' が付いてた
                    pms[p].param = op       # '=xxxx' の 'xxxx' をパラメータに格納

                elif pms[p].needParam:      # オプションパラメータ必要
                    if op := tm.getOpParam():   # 次のブロックをオプションパラメータとして読む
                        pms[p].param = op
                    else:
                        err = ('E1', p)     # E1: Argument expected for the -<p>
                        break
            else:
                err = ('E0', p)     # E0: Unknown option: -<p>

        else:                           # コマンドパラメータブロック
            if tm.isEndBlock():         # 多分前のブロックが '--' だった
                tm.transNext()
            param = tm.getAll()
            __params.append(param)

            if partial_mode == PARTIAL:     # 個別モードだったらここで一旦終了
                tm.transNext()
                return err

        if tm.isEndBlock():
            tm.transNext()

        if err:
            if error_mode <= ERROR_CONT:
                print(Eset.Errmsg(err), file=error_output)
            if error_mode == ERROR_END:
                sys.exit(error_code)
            return err
            # break
    return err


if __name__ == "__main__":
    partial_mode = PARTIAL
    error_code = 1
    pm = {'a': Oset(False, False, 'comment for a'),
          'L': Oset(False, True, 'Lのコメント'),
          'f': Oset(False, False, 'これがfです'),
          'l': Oset(False, False, 'これがlです'),
          'verbose': Oset(False, True, '静かにね'),
          }

    printOset(pm)
    print('----')

    ret = []
    myArgs = Args(sys.argv)
    ret = miniparse(myArgs, pm)
    print('----')
    print(ret)
    print(myArgs.remainArgs())
    printOset(pm)
    for i, p in enumerate(params()):
        print(i, p)

    ret = miniparse(myArgs, pm)
    print('----')
    print(ret)
    print(myArgs.remainArgs())
    printOset(pm)
    for i, p in enumerate(params()):
        print(i, p)
