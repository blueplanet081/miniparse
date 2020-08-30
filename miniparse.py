from typing import TextIO, Union, List, Dict, Tuple, Optional
import sys
import pathlib
from enum import Enum
'''
miniparse.py コマンドライン解析モジュール
version 0.5ぐらい
2020/8/27 by te.
'''

''' <:=>は外したので、Python 3.7 でも動きます。それより前は試していません。 '''
# if sys.version_info < (3, 8):
#     print('このモジュールは、Python 3.8以降に対応しています。ごめんなさい。')
#     print('もし、モジュール内の <:=> 演算子部分を2行に書き換えれば、3.7以前でも動くかもしれません。')
#     sys.exit()


# 全部モード(WHOLE)、個別モード(PARTIAL)
# 個別モードのときは、コマンドパラメータを検出した時に一旦終了する。
# 　--> command -axL param next --continue　の、param、next検出時など
class Pmode(Enum):
    ''' 全部モード(WHOLE)、個別モード(PARTIAL) '''
    WHOLE = 0       # 全部モード
    PARTIAL = 1     # 個別モード

partial_mode: Pmode = Pmode.WHOLE   # noqa


# エラーを検出したときにどうするか
class Emode(Enum):
    ''' エラー出力＆終了(ERROR_END)、エラー出力続行(ERROR_CONT)、サイレント続行(SILENT_CONT) '''
    ERROR_END = 0       # エラーを出力して終了
    ERROR_CONT = 1      # エラーを出力して続行（miniparse() の戻り値がエラーID）
    SILENT_CONT = 2     # エラーを出さずに続行（miniparse() の戻り値がエラーID）

error_mode: Emode = Emode.ERROR_END    # noqa


# エラー出力時に usage: を出力するかどうか
class Umode(Enum):
    ''' エラー出力時に、usage:を出力しない(NONE)、usage:行のみ出力(USAGE)、
        オプションリストも出力(OPTIONLIST)
    '''
    NONE = 0        # 出力しない
    USAGE = 1       # usage行のみ出力
    USAGE_AND_OPTION = 2    # usage行と、オプションリストを出力

usage_mode: Umode = Umode.USAGE_AND_OPTION      # noqa

# エラー終了時のコード
error_code = 1
# エラーメッセージ出力先
error_output: TextIO = sys.stderr


# -------------------------------------------------------------
# コマンドラインオプション情報を格納するclassとか、関連のfunctionの定義
# コマンドラインオプション情報自体は、ユーザプログラム側で定義する。
# -------------------------------------------------------------

class Oset():
    def __init__(self, isTrue: bool = False, needArg: bool = False,
                 Argcomment: str = '', comment: str = ''):
        ''' コマンドラインオプション情報を格納するclass
        '''
        self.isTrue = isTrue            # オプション状態(省略時は False、指定されていれば True)
        self.needArg = needArg          # オプションアーギュメントが必須か(省略時は False)
        self.opArg = ''                 # 指定されたオプションアーギュメント(初期値はナシ = 空白)
        self.Argcomment = Argcomment    # オプションアーギュメントの意味
        self.comment = comment          # オプションの意味


Topset = Dict[str, Oset]                # オプションセットのType


def make_usage(comName: str, ops: Topset) -> str:
    ''' コマンドラインオプション情報から、usage: メッセージを作成する
    '''
    pstr = f'usage: {comName} '                 # コマンド名
    # if pp1 := [pp for pp in pm if len(pp) == 1 and not ops[pp].needArg]:
    pp1 = [pp for pp in ops if len(pp) == 1 and not ops[pp].needArg]
    if pp1:
        pstr += ' -'                            # １文字オプション
        for p in pp1:
            pstr += p
    for p in [pp for pp in ops if len(pp) == 1 and ops[pp].needArg]:
        pstr += f' -{p}{ops[p].Argcomment}'     # １文字オプションでアーギュメントあり
    for p in [pp for pp in ops if len(pp) > 1]:
        pstr += f' --{p}'                       # 複数文字オプション
        if ops[p].Argcomment:                   # 複数文字オプションでアーギュメントあり
            pstr += f'={ops[p].Argcomment}'
    if '' in ops:                               # コマンドアーギュメント
        pstr += f"    {ops[''].Argcomment}"
    return pstr


def make_plist(ops: Topset) -> List[str]:
    ''' コマンドラインオプション情報から、オプション一覧listを作成する
    '''
    plist = []
    indent = 2
    for pp in ops:
        if len(pp) == 1:
            if ops[pp].needArg:                 # １文字オプションでアーギュメントあり
                plist.append(' ' * indent + '-{0} {1}: {2}'
                             .format(pp, ops[pp].Argcomment, ops[pp].comment))
            else:                               # １文字オプションでアーギュメントなし
                plist.append(' ' * indent + '-{0}: {1}'.format(pp, ops[pp].comment))
        elif len(pp) > 1:
            if ops[pp].Argcomment != '':        # 複数文字オプションでアーギュメントあり
                plist.append(' ' * indent + '--{0}={1}: {2}'
                             .format(pp, ops[pp].Argcomment, ops[pp].comment))
            else:                               # 複数文字オプションでアーギュメントなし
                plist.append(' ' * indent + '--{0}: {1}'
                             .format(pp, ops[pp].comment))
    return plist


def printUsage(comName: str, ops: Topset, umode: Umode, output: TextIO = sys.stdout):
    ''' usage:情報の出力。
        (umode=Umode.USAGE usage:行のみ、Umode.USAGE_AND_OPTION usage:行とオプションリストを出力)
    '''
    if umode in (Umode.USAGE, Umode.USAGE_AND_OPTION):
        print(make_usage(comName, ops), file=output)
    if umode == Umode.USAGE_AND_OPTION:
        for pl in make_plist(ops):
            print(pl, file=output)
    print(file=error_output)


def printOset(ops: Topset) -> None:
    ''' コマンドラインオプション情報の一覧を表示する（デバッグ用）
    '''
    print('option [.isTrue] .needArg [.opArg] "Argcomment" ".comment"')
    for pp in ops:
        print(pp.ljust(8),
              '[' + str(ops[pp].isTrue).ljust(5) + ']',
              str(ops[pp].needArg).ljust(8),
              '[' + ops[pp].opArg + ']',
              '"' + ops[pp].Argcomment + '"',
              '"'+ops[pp].comment+'"')


# -------------------------------------------------------------
# エラーメッセージ情報を格納するclassとか、関連のfunctionの定義
# 基本のエラーメッセージ情報は本モジュール内で定義されており、
# ユーザは必要に応じて個々のメッセージ情報を変更したり、追加したりできる
# -------------------------------------------------------------

class Eset():
    def __init__(self, emsg: str):
        ''' エラーメッセージ情報を格納するclass
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


Es = {'E0': Eset("Command argument expected"),
      'E1': Eset("Unkown option: -{0}"),
      'E2': Eset("Argument expected for the -{0} option"),
      'U0': Eset("Your message here {0} of {1}"),
      }


# -------------------------------------------------------------
# コマンドライン解析用classの定義
# あらかじめコマンドライン全体をコピーし、順次解析用に使う
# -------------------------------------------------------------

class Args():
    ''' コマンドライン解析用class
    '''
    def __init__(self, args: List[str]):
        ''' コマンドライン解析用インスタンスを作成
        '''
        self.__cmdPath = args[0]    # コマンドパス名
        self.__args = args[1:]      # 解析用コマンドパラメータ
        self.__num = 0              # 解析中ブロックポインタ
        self.__pos = 0              # 解析中ブロック内ポインタ

    def getCommandPath(self) -> str:
        ''' コマンドパス名を返す
        '''
        return self.__cmdPath

    def getCommandName(self) -> str:
        ''' コマンド名を返す
        '''
        p = pathlib.Path(self.__cmdPath)
        return p.name

    def popOptionType(self) -> str:
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
            return ''           # コマンドアーギュメントブロック

    def popOne(self) -> str:
        ''' シングルオプションブロックから１文字取り出す
        '''
        tpos = self.__pos
        self.__pos += 1
        # print(tpos, self.__num)
        return self.__args[self.__num][tpos:tpos + 1]

    def popLong(self) -> str:
        ''' ロングオプションブロックから、オプションを取り出す
        '''
        tpos = self.__pos
        # if (ppos := self.__args[self.__num][tpos:].find('=')) == -1:
        ppos = self.__args[self.__num][tpos:].find('=')
        if ppos == -1:
            self.__pos = len(self.__args[self.__num])
            return self.__args[self.__num][tpos:]
        else:               # 後ろに '=xxx' のオプションパラメータあり
            self.__pos = tpos + ppos + 1
            return self.__args[self.__num][tpos:tpos + ppos]

    def popAllblock(self) -> str:
        ''' 引数ブロックの全体、または残りを取り出す
        '''
        lpos = self.__pos
        self.__pos = len(self.__args[self.__num])
        return self.__args[self.__num][lpos:]

    def popOpArg(self) -> str:
        ''' 次のブロックのオプションパラメータを取得する
        '''
        if self.transNext():
            if self.popOptionType() == '--' and self.isEndBlock():
                if self.transNext():
                    return self.popAllblock()
                else:
                    return ""
            elif self.popOptionType() == '':
                return self.popAllblock()
            # 次のブロックが無かったり、パラメータブロックだったら取得失敗
        return ""

    def getRemainArgs(self) -> List[str]:
        ''' 解析中のコマンドラインの残りを返す（解析位置等は更新されない）
        '''
        return self.__args[self.__num:]

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


# -------------------------------------------------------------
# コマンドライン解析用function の定義
# -------------------------------------------------------------

__arguments = []
''' 取得したパラメータの格納用
'''

def arguments() -> List[str]:   # noqa
    ''' 取得したパラメータのリストを返す
    '''
    return __arguments


TparseError = Optional[Tuple[str, ...]]     # エラーType

# def miniparse(tm: 'Args', ops: Dict[str, Oset]) -> TparseError:  # noqa
def miniparse(args: Args, ops: Topset) -> TparseError:  # noqa
    ''' コマンドライン解析用モジュール
    '''
    err: TparseError = None
    while not args.isAllEnd():
        if args.popOptionType() == '-':     # シングルオプションブロック
            # while p := args.popOne():
            while True:
                p = args.popOne()
                if not p:
                    break
                if p in ops:
                    ops[p].isTrue = True
                    if ops[p].needArg:      # オプションパラメータ必要
                        # if op := args.popAll():
                        op = args.popAllblock()
                        if op:
                            ops[p].opArg = op
                        # elif op := args.popOpArg():
                        else:
                            op = args.popOpArg()
                            if op:
                                ops[p].opArg = op
                            else:
                                err = ('E2', p)     # E2: Argument expected for the -<p>
                        break
                else:
                    err = ('E1', p)     # E1: Unknown option: -<p>
                    args.popAllblock()  # エラーなので、ブロックの残りを空読み
                    break

        # elif args.optionType() == '--' and (p := args.popLong()):   # ロングオプションブロック
        elif args.popOptionType() == '--':
            p = args.popLong()
            if p:
                if p in ops:
                    ops[p].isTrue = True
                    # if op := args.popAllblock():  # ブロックの後ろがまだあった -->'=xxxx' が付いてた
                    op = args.popAllblock()
                    if op:
                        ops[p].opArg = op       # '=xxxx' の 'xxxx' をパラメータに格納

                    elif ops[p].needArg:        # オプションパラメータ必要
                        # if op := args.popOpArg():   # 次のブロックをオプションパラメータとして読む
                        op = args.popOpArg()
                        if op:
                            ops[p].opArg = op
                        else:
                            err = ('E2', p)     # E2: Argument expected for the -<p>
                            break
                else:
                    err = ('E1', p)     # E1: Unknown option: -<p>

        else:                       # コマンドパラメータブロック
            if args.isEndBlock():       # 多分前のブロックが '--' だった
                args.transNext()
                if args.isAllEnd():         # と思ったら次のブロックが無かった
                    break
            param = args.popAllblock()  # コマンドアーギュメント取得
            __arguments.append(param)
            if '' in ops:
                ops[''].isTrue = True
                ops[''].opArg = param

            if partial_mode == Pmode.PARTIAL:   # 個別モードだったらここで一旦終了
                args.transNext()
                return err

        if args.isEndBlock():
            args.transNext()

        if err:
            break

    if not err:     # 今までエラーが無くて、
        if '' in ops and ops[''].needArg and not ops[''].opArg:
                    # noqa コマンドアーギュメントが必要で、でもコマンドアーギュメントが無い
            err = ('E0',)   # E0: Command argument expected

    if err:     # エラー検出時処理
        if error_mode in (Emode.ERROR_CONT, Emode.ERROR_END):
            print(Eset.Errmsg(err), file=error_output)
            printUsage(args.getCommandName(), ops, usage_mode, error_output)
        if error_mode == Emode.ERROR_END:
            sys.exit(error_code)

    return err
# -------------------------------------------------------------
# 定義終了
# -------------------------------------------------------------


if __name__ == "__main__":
    partial_mode = Pmode.WHOLE
    usage_mode = Umode.USAGE_AND_OPTION
    error_code = 1

    pm = {'': Oset(False, True, 'ディレクトリ', ''),
          'a': Oset(False, False, '', 'comment for a'),
          'L': Oset(False, True, '階層数', 'Lのコメント'),
          'f': Oset(False, False, '', 'これがfです'),
          'l': Oset(False, False, '', 'これがlです'),
          'h': Oset(False, False, '', '使い方を表示'),
          'verbose': Oset(False, True, 'あれの長さ', '静かにね'),
          }

    myArgs = Args(sys.argv)
    err = miniparse(myArgs, pm)

    if pm['h'].isTrue:
        print('このプログラムは、モジュール miniparse の使い方を示すものです。')
        printUsage(myArgs.getCommandName(), pm, Umode.USAGE_AND_OPTION)

    print()
    print('----')
    printOset(pm)

    print('----')

    if err:
        print('コマンドライン中にエラーがありました。')
        print(Eset.Errmsg(err))

    for p in pm:
        if len(p) == 1 and pm[p].isTrue:
            if pm[p].opArg:
                print(f'option -{p} {pm[p].opArg} が指定されました。')
            else:
                print(f'option -{p} が指定されました。')
        elif len(p) > 1 and pm[p].isTrue:
            if pm[p].opArg:
                print(f'option --{p}={pm[p].opArg} が指定されました。')
            else:
                print(f'option --{p} が指定されました。')

    print()
    print(f'コマンドラインアーギュメントとして、{arguments()} が指定されました。')
