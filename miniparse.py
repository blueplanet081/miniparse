from typing import TextIO, Union, List, Dict, Tuple, Optional, Iterator
import sys
import pathlib
from enum import Enum, auto
import platform
import glob

'''
miniparse.py コマンドライン解析モジュール
version 0.8ぐらい、一部機能を外した暫定版
2020/9/3 by te.
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

# アーギュメント展開用にシステム判定
isWin = True if platform.system() == 'Windows' else False


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


def __getWild(wild: str) -> List[str]:
    ''' ホームディレクトリ '~'、ワイルドカードを展開して、リストで返す。
        頭にハイフンが付いているもの、ワイルドカードに展開できないものはそのまま返す
        （その時は、文字列が一つのリストになる）
    '''
    ret = []
    if wild.startswith('-'):
        ret.append(wild)
        return ret
    if wild.startswith('~'):
        wild = str(pathlib.Path.home()) + wild[1:]
        print(wild)

    if '*' in wild or '?' in wild or ('[' in wild and len(wild) > 1):
        for w in glob.glob(wild):
            ret.append(w)
        if not ret:
            ret.append(wild)
    else:
        ret.append(wild)
    return ret


def wArgs(__args: List[str]) -> List[str]:
    ''' 渡されたリスト中の項目を、ワイルドカード展開する
    '''
    ret = []
    for p in __args:
        ret += __getWild(p)
    return ret


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


class Ptype(Enum):  # パーツタイプ
    ''' コマンドライン解析用パーツタイプ
        (BLOCK, SOPT, SSEP, LOPT)
    '''
    BLOCK = auto()      # 普通のブロック
    SOPT = auto()       # ショートオプション
    SSEP = auto()       # ショートオプションの終わり
    LOPT = auto()       # ロングオプション


def getOps(__args: List[str]) -> Iterator[Tuple[int, Ptype, str]]:
    ''' コマンドラインを解析用パーツに分解してタプルで返す。
        （元のリスト番号, Ptype, コンテンツ）
    '''
    i_args = iter(__args)
    for i, ob in enumerate(i_args):
        if ob == '--':                      # 強制ブロック（'--' の次のブロック）
            ob = next(i_args, '')
            yield i, Ptype.BLOCK, ob
        elif ob.startswith('--'):           # ロングオプションブロック
            yield i, Ptype.LOPT, ob[2:]
        elif ob.startswith('-'):            # ショートオプションブロック
            sblock = ob[1:]
            for pp in sblock:               # 分解されたショートオプション
                yield i, Ptype.SOPT, pp
            yield i, Ptype.SSEP, sblock     # ショートオプションの終わり
        else:                               # 普通のブロック
            yield i, Ptype.BLOCK, ob


def miniparse(args: List[str,], ops: Topset) -> TparseError:  # noqa
    ''' コマンドライン解析用モジュール
    '''
    err: TparseError = None
    is_needArg = False
    is_needArgBlock = False
    needArgP = ''
    print(args)

    for i, ptype, p in getOps(args):
        print(i, ptype, p)
        if is_needArgBlock:                 # オプション引数のブロック待ちだった
            if ptype == Ptype.BLOCK:            # 普通ブロック来た
                ops[needArgP].opArg = p
                is_needArgBlock = False
            else:                               # 普通ブロックが来なかった
                err = ('E2', p)     # E2: Argument expected for the -<p>
                break
            continue

        if ptype == Ptype.BLOCK:            # 普通のブロック
            __arguments.append(p)               # コマンド引数として格納
            if '' in ops:
                ops[''].isTrue = True
                ops[''].opArg = p

        elif ptype == Ptype.SOPT:           # ショートオプションブロック
            if is_needArg:                      # オプション引数待ち
                pass
            elif p in ops:                      # オプション判定
                ops[p].isTrue = True
                if ops[p].needArg:                  # オプション引数必要
                    is_needArg = True               # オプション引数待ちをセット
                    needArgP = p
                    ops[needArgP].opArg = ''
            else:                               # Unknown option
                err = ('E1', p)     # E1: Unknown option: -<p>
                break

        elif ptype == Ptype.SSEP:           # ショートオプションブロックの終わり
            if is_needArg:                  # オプション引数待ち
                ops[needArgP].opArg = p[p.find(needArgP)+1:]
                if ops[needArgP].opArg:     # オプション引数あった
                    is_needArg = False
                else:
                    is_needArgBlock = True

        elif ptype == Ptype.LOPT:           # ロングオプションブロック
            ppos = p.find('=')
            if ppos != -1:                  # 引数（option=arg）あり
                pwork = p[ppos+1:]
                p = p[:ppos]
                print(p, pwork)
            else:                           # 引数なし
                pwork = ''
            if p in ops:                    # オプション判定
                ops[p].isTrue = True
                ops[p].opArg = pwork
                if ops[p].needArg and not pwork:    # オプション引数必要
                    is_needArgBlock = True
                    needArgP = p
            else:                           # Unknown option
                err = ('E1', p)     # E1: Unknown option: -<p>
                print("オプション p はダメ！！")
                break

    if not err:     # 今までエラーが無くて、
        if '' in ops and ops[''].needArg and not ops[''].opArg:
                    # noqa コマンドアーギュメントが必要で、でもコマンドアーギュメントが無い
            err = ('E0',)   # E0: Command argument expected

    if err:     # エラー検出時処理
        if error_mode in (Emode.ERROR_CONT, Emode.ERROR_END):
            print(Eset.Errmsg(err), file=error_output)
            # printUsage(args.getCommandName(), ops, usage_mode, error_output)
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

    myArgs = wArgs(sys.argv)
    err = miniparse(myArgs[1:], pm)

    if pm['h'].isTrue:
        print('このプログラムは、モジュール miniparse の使い方を示すものです。')
        # printUsage(myArgs.getCommandName(), pm, Umode.USAGE_AND_OPTION)

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
