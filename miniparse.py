from typing import KeysView, TextIO, Union, List, Dict, Tuple, Optional, Iterator
import sys
import pathlib
from enum import Enum, Flag, auto
import platform
import glob

'''
miniparse.py コマンドライン解析モジュール
version 永遠の 0.9、一応機能満載版
動作条件 Python 3.7以降（Enum が動けば 3.6でも動くかも）
2020/9/15 by te.
'''


# 全部モード(WHOLE)、個別モード(PARTIAL)、
# 引数までで一旦区切りモード(ARG)     command -F params | -bx params2 | -f ....
# オプションで一旦区切りモード(OPT)   command -F | params -bx | params2 -f |
# （| ← 区切り箇所）
class Smode(Enum):
    ''' 全部モード(WHOLE)、個別モード(PARTIAL)、
        引数区切りモード(ARG)、オプション区切りモード(OPT)
    '''
    WHOLE = auto()      # 全部モード
    EVERY = auto()      # 個別モード
    ARG = auto()        # 引数区切りモード
    OPT = auto()        # オプション区切りモード


separation_mode: Smode = Smode.WHOLE   # noqa


# エラーを検出したときにどうするか
class Emode(Enum):
    ''' エラー出力＆終了(ERROR_END)、エラー出力続行(ERROR_CONT)、サイレント続行(SILENT_CONT) '''
    ERROR_END = auto()       # エラーを出力して終了
    ERROR_CONT = auto()      # エラーを出力して続行（エラーコードは get_parseError() で取得）
    SILENT_CONT = auto()     # エラーを出さずに続行（エラーコードは get_parseError() で取得）

error_mode: Emode = Emode.ERROR_END    # noqa


# エラー出力時に usage: を出力するかどうか
class Umode(Flag):
    ''' エラー出力時に、usage:を出力しない(NONE)、usage:行のみ出力(USAGE)、
        オプションリストのみ出力(OLIST)、両方とも出力(BOTH)
    '''
    NONE = auto()           # 出力しない
    USER = auto()           # ユーザ指定のメッセージを出力
    USAGE = auto()          # usage行のみ出力
    OLIST = auto()          # オプションリストを出力
    BOTH = USAGE | OLIST    # usage: とオプションリストの両方を出力

usage_mode: Umode = Umode.BOTH      # noqa
usage_usermessage = ''      # ユーザー指定のメッセージ（上書きする）

# エラー終了時のコード
error_code = 1
# エラーメッセージ出力先
error_output: TextIO = sys.stderr


# -------------------------------------------------------------
# ワイルドカード展開モジュール（一応汎用、Windows専用）
# -------------------------------------------------------------

# Windowsかどうか判定
isWin = True if platform.system() == 'Windows' else False


def __getWild(wild: str) -> List[str]:
    ''' ホームディレクトリ '~'、ワイルドカードを展開して、リストで返す。
        頭にハイフンが付いているもの、ワイルドカードに展開できないものはそのまま返す
        （その時は、要素が１つのリストになる）
    '''
    ret = []
    if wild.startswith(' ') or wild.startswith('\\'):
        ret.append(wild[1:])
        return ret
    if wild.startswith('~'):
        wild = str(pathlib.Path.home()) + wild[1:]

    if '*' in wild or '?' in wild or ('[' in wild and len(wild) > 1):
        for w in glob.glob(wild):
            ret.append(w)
        if not ret:
            ret.append(wild)
    else:
        ret.append(wild)
    return ret


def _wArgs(__args: List[str]) -> List[str]:
    ''' 渡されたリスト中の項目をワイルドカード展開する
    '''
    ret = []
    for p in __args:
        ret += __getWild(p)
    return ret


# -------------------------------------------------------------
# ターンチェック（一応、汎用クラス）
# -------------------------------------------------------------

class Turn(Enum):
    OPT = auto()    # オプション・ターン
    ARG = auto()    # 引数・ターン


class CheckTurn():
    def __init__(self):
        ''' ターンをチェックするクラス
        '''
        self.__turn = None
        self.__turncheck = False

    def checkTurn(self, turn: Optional[Enum] = None) -> bool:
        ''' ターンの状態をチェックする。前回のターンから変わったら True（初回は False）。
            引数省略時は、現在の状態を返す
        '''
        if turn:
            self.__turncheck = True if self.__turn and self.__turn is not turn else False
            self.__turn = turn
        return self.__turncheck

    def getTurn(self) -> Optional[Enum]:
        ''' 現在のターンを返す
        '''
        return self.__turn


# -------------------------------------------------------------
# コマンドラインオプション情報を格納するclassとか、関連のfunctionの定義
# コマンドラインオプション情報自体は、ユーザプログラム側で定義する。
# -------------------------------------------------------------

class Oinfo():
    def __init__(self, needArg: bool = False,
                 Argcomment: str = '', comment: str = ''):
        ''' 個々のコマンドラインオプション情報を格納するclass
        '''
        self.needArg = needArg          # オプション引数が必須か
        self.Argcomment = Argcomment    # オプション引数の説明(Usage、オプションリスト用)
        self.comment = comment          # オプションの説明（オプションリスト用）
        ''' 以下はmniparse()の処理で取得 '''
        self.isTrue = False             # オプションが指定されたら True
        self.opArg: List[str] = []      # 入力されたオプション引数のリスト


TypeOpList = List[Union[Tuple[str],     # オプション情報定義用の Type
                        Tuple[str, bool],
                        Tuple[str, bool, str],
                        Tuple[str, bool, str, str],
                        ]
                  ]


class OpSet():
    ''' オプション情報管理クラス '''
    def __init__(self, pms: TypeOpList):
        ''' オプション管理情報の作成 '''
        self.op: Dict[str, Oinfo] = {}
        for pm in pms:                  # 注）同名オプションは上書きされる
            pmax = len(pm)
            self.op[pm[0]] = Oinfo(bool(pm[1]) if pmax > 1 else False,
                                   pm[2] if pmax > 2 else '',
                                   pm[3] if pmax > 3 else '',
                                   )

    def get_keys(self) -> KeysView[str]:
        ''' key（オプション）一覧を返す
        '''
        return self.op.keys()

    def reset_data(self):
        ''' 取得したデータをリセットする（使用注意！！）
        '''
        for key in self.get_keys():
            self.op[key].isTrue = False
            self.op[key].opArg = []

    def isExist(self, key: str) -> bool:
        ''' そのオプションが指定のオプション情報中にあるかどうか
        '''
        return key in self.op

    def _get_Longoption(self, key: str) -> str:
        ''' 入力に一致するロングオプションkeyを取得する。無ければ空文字。
            （一意に判定できる省略形を許容する）
        '''
        if key[1:] and key in self.op.keys():           # 2文字以上で完全一致
            return key
        keep = ''
        for lk in [k for k in self.op.keys() if k[1:]]:
            if lk.startswith(key):                           # 省略形だった
                if keep:                                     # 一意で無かった
                    return key
                keep = lk                                    # 完全形をキープ
        return keep             # 一意であればそのkeyが入っている。無ければ空文字

    def _set_True(self, key: str) -> bool:
        ''' そのオプションが指定（入力）されたことをセットする
        '''
        if key in self.op:
            self.op[key].isTrue = True
            return True
        return False

    def isTrue(self, key: str) -> bool:
        ''' そのオプションが指定（入力）されたかどうか
        '''
        if key in self.op:
            return self.op[key].isTrue
        return False

    def isNeedArg(self, key: str) -> bool:
        ''' そのオプションに引数が必須かどうか
        '''
        if key in self.op:
            return self.op[key].needArg
        return False

    def _append_opArg(self, key: str, oparg: str) -> None:
        ''' 指定されたオプションの引数をリストに格納する
        '''
        if key in self.op:
            self.op[key].opArg.append(oparg)

    def get_opArg(self, key: str) -> List[str]:
        ''' 指定されたオプションの引数リストを取得する
        '''
        if key in self.op:
            return self.op[key].opArg
        return []

    def get_Argcomment(self, key: str) -> str:
        ''' そのオプションの引数の説明取得する
        '''
        if key in self.op:
            return self.op[key].Argcomment
        return ''

    def get_comment(self, key: str) -> str:
        ''' そのオプションの説明取得する
        '''
        if key in self.op:
            return self.op[key].comment
        return ''


TypeOpset = Dict[str, Oinfo]                # オプションセットのType


def make_usage(comName: str, ops: OpSet) -> str:
    ''' コマンドラインオプション情報から、簡易的な usage: メッセージを作成する。
        comNameが空文字列の時は、内部で確保しているコマンド名を使用する
    '''
    if not comName:
        comName = pathlib.Path(GLOBAL_commandPath).name
    pstr = f'usage: {comName} '             # コマンド名
    p1s = [p for p in ops.get_keys() if len(p) == 1 and not ops.isNeedArg(p)]
    if p1s:                                 # 1文字オプション（引数なし）
        pstr += ' -'
        for p1 in p1s:
            pstr += p1
    for p1 in [p for p in ops.get_keys() if len(p) == 1 and ops.isNeedArg(p)]:
        pstr += f' -{p1}{ops.get_Argcomment(p1)}'   # １文字オプション＋引数
    for pl in [p for p in ops.get_keys() if len(p) > 1]:
        pstr += f' --{pl}'                          # 複数文字オプション
        if ops.get_Argcomment(pl):                  # 複数文字オプションの引数（あれば）
            pstr += f'={ops.get_Argcomment(pl)}'
    if ops.isExist(''):                     # コマンド引数
        pstr += f"    {ops.get_Argcomment('')}"
    return pstr


def make_plist(ops: OpSet) -> str:
    ''' コマンドラインオプション情報から、オプション一覧リスト（文字列）を作成する
    '''
    plist: str = ''
    indent = 2
    for pp in ops.get_keys():
        if pp == '':
            continue
        argcomment = ops.get_Argcomment(pp)
        if len(pp) == 1:                            # 1文字オプション( -a -L みたいな)
            plist += ' ' * indent + '-' + pp
            plist += (' ' + argcomment + ':  ') if ops.isNeedArg(pp) and argcomment else ': '
        elif len(pp) > 1:                           # 複数文字オプション( --verbose みたいな)
            plist += ' ' * indent + '--' + pp
            if argcomment:
                plist += ('=' + argcomment if ops.isNeedArg(pp)
                          else '[=' + argcomment + ']') + ':  '
            else:
                plist += ': '
        plist += ops.get_comment(pp) + '\n'

    return plist[0:-1]


def printUsage(comName: str, ops: OpSet, umode: Umode, output: TextIO = sys.stdout):
    ''' usage:情報の出力。
        (umode=Umode.USAGE usage:行のみ、Umode.USAGE_AND_OPTION usage:行とオプションリストを出力)
    '''
    if Umode.USER in umode and usage_usermessage:
        print(usage_usermessage, file=output)
    if Umode.USAGE in umode:
        print(make_usage(comName, ops), file=output)
    if Umode.OLIST in umode:
        print(make_plist(ops), file=output)
    print(file=error_output)


def printOpset(opp: OpSet) -> None:
    ''' コマンドラインオプション情報の一覧を適当に表示する（デバッグ用）
    '''
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


# -------------------------------------------------------------
# コマンドライン解析時のエラーメッセージを生成するデータと関数
# 基本のエラーメッセージ情報（原文）は以下で定義されており、
# メッセージを変えたかったら上書きで変更してください。
# -------------------------------------------------------------

Eset = {'E0': "Command argument expected",
        'E1': "Unknown option: {0}",
        'E2': "Argument expected for the {0} option",
        'U0': "Your message here {0} of {1}",
        }


def make_errmsg(ueid: Union[str, Tuple[str, ...]], p0: str = 'p0', p1: str = 'p1') -> str:
    ''' エラーメッセージを生成する
    '''
    if type(ueid) is tuple:
        eid = ueid[0] if len(ueid) > 0 else 'XX'
        p0 = ueid[1] if len(ueid) > 1 else 'p0'
        p1 = ueid[2] if len(ueid) > 2 else 'p1'
    else:
        eid = ueid
    if eid in Eset:
        return Eset[eid].format(p0, p1)
    else:
        return f"***Undefined message {eid}: <{p0}> <{p1}>"


# -------------------------------------------------------------
# コマンドライン解析用function の定義
# -------------------------------------------------------------

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
        elif ob.startswith('-') and ob[1:]:            # ショートオプションブロック
            sblock = ob[1:]
            for pp in sblock:               # 分解されたショートオプション
                yield i, Ptype.SOPT, pp
            yield i, Ptype.SSEP, sblock     # ショートオプションの終わり
        else:                               # 普通のブロック
            yield i, Ptype.BLOCK, ob


# -------------------------------------------------------------
# 秘密のGLOBAL定義
# -------------------------------------------------------------

GLOBAL_arguments = []           # 取得したパラメータの格納用
def get_arguments() -> List[str]:   # noqa
    ''' 取得したパラメータのリストを返す
    '''
    return GLOBAL_arguments


TypeParseError = Optional[Tuple[str, ...]]     # エラーType
GLOBAL_err: TypeParseError = None       # オプションエラー格納用
def get_parseError() -> TypeParseError:     # noqa
    ''' 解析エラーを返す
    '''
    return GLOBAL_err


# -------------------------------------------------------------
# 解析メイン（miniparse）
# -------------------------------------------------------------

def miniparse_0(ops: OpSet, args: List[str,]) -> Iterator[Tuple[int, Optional[Enum]]]:  # noqa
    ''' コマンドライン解析用モジュール
    '''
    global GLOBAL_arguments             # 取得したパラメータの格納用
    global GLOBAL_err                   # オプションエラー格納用

    t = CheckTurn()     # オプション解析中(Turn.OPT)、引数解析中（Turn.ARG）

    is_needArg = False
    is_needArgBlock = False
    needArgP = ''

    # print(args)

    for i, ptype, p in getOps(args):
        # print(i, ptype, p)
        if is_needArgBlock:                 # オプション引数のブロック待ちだった
            if ptype == Ptype.BLOCK:            # 普通ブロック来た
                ops._append_opArg(needArgP, p)
                is_needArgBlock = False
            else:                               # 普通ブロックが来なかった
                whyphen = '--' if needArgP[1:] else '-'
                GLOBAL_err = ('E2', whyphen + needArgP)   # E2: Argument expected for the -<p>
                break
            continue

        if ptype == Ptype.BLOCK:            # 普通のブロック
            GLOBAL_arguments.append(p)      # コマンド引数として格納

            if t.checkTurn(Turn.ARG):           # ★★引数解析のターン
                yield i, t.getTurn()

            if ops.isExist(''):
                ops._set_True('')
                ops._append_opArg('', p)

        elif ptype == Ptype.SOPT:           # ショートオプションブロック
            if t.checkTurn(Turn.OPT):           # ★★引数解析のターン
                yield i, t.getTurn()

            if is_needArg:                      # オプション引数待ち
                pass

            elif ops.isExist(p):                    # オプション判定
                ops._set_True(p)
                if ops.isNeedArg(p):                # オプション引数必要
                    is_needArg = True                   # オプション引数待ちをセット
                    needArgP = p
                    # ops.append_opArg(needArgP, '')
            else:                               # Unknown option
                GLOBAL_err = ('E1', '-' + p)    # E1: Unknown option: -<p>
                break

        elif ptype == Ptype.SSEP:           # ショートオプションブロックの終わり
            if is_needArg:                  # オプション引数待ち
                w_oparg = p[p.find(needArgP)+1:]
                is_needArg = False
                if w_oparg:                 # オプション引数あった
                    ops._append_opArg(needArgP, w_oparg)
                else:
                    is_needArgBlock = True

        elif ptype == Ptype.LOPT:           # ロングオプションブロック

            if t.checkTurn(Turn.OPT):           # ★★引数解析のターン
                yield i, t.getTurn()

            ppos = p.find('=')
            if ppos != -1:                  # 引数（option=arg）あり
                pwork = p[ppos+1:]
                p = p[:ppos]
            else:                           # 引数なし
                pwork = ''

            wp = ops._get_Longoption(p)     # 一致するロングオプションkeyを取得
            if wp:
                ops._set_True(wp)
                if pwork:                   # オプション(=xxx)ついてたか
                    ops._append_opArg(wp, pwork)
                elif ops.isNeedArg(wp):     # オプション必須か
                    is_needArgBlock = True
                    needArgP = wp
            else:                           # Unknown option
                GLOBAL_err = ('E1', '--' + p)      # E1: Unknown option: --<p>
                break

    if not GLOBAL_err:     # 今までエラーが無くて、
        if ops.isExist('') and ops.isNeedArg('') and not ops.get_opArg(''):
                    # noqa コマンドアーギュメントが必要で、でもコマンドアーギュメントが無い
            GLOBAL_err = ('E0',)   # E0: Command argument expected

    if GLOBAL_err:     # エラー検出時処理
        if error_mode in (Emode.ERROR_CONT, Emode.ERROR_END):
            print(make_errmsg(GLOBAL_err), file=error_output)
            printUsage("", ops, usage_mode, error_output)
        if error_mode == Emode.ERROR_END:
            sys.exit(error_code)

    yield -1, None


# -------------------------------------------------------------
# コマンドライン解析モジュール・フロントエンド部
# -------------------------------------------------------------

GLOBAL_iterMP = None            # イテレータ(miniparse_0)呼び出し用
GLOBAL_iterEnd = False          # イテレータ(miniparse_0)終了フラグ

GLOBAL_commandPath = ''         # コマンドpath 退避用
GLOBAL_args = []                # 解析中コマンドライン退避用
GLOBAL_pos = 0                  # 解析中のコマンドライン（リスト）位置


def get_remainArgs() -> List[str]:
    ''' 解析中の残りのコマンドラインを取得する
    '''
    if GLOBAL_pos == -1:
        return []
    return GLOBAL_args[GLOBAL_pos:]


def miniparse(ops: Optional[OpSet] = None, arg: List[str, ] = []) -> bool:
    ''' コマンドライン解析モジュール・フロントエンド
    '''
    global GLOBAL_iterMP
    global GLOBAL_iterEnd
    global GLOBAL_commandPath
    global GLOBAL_args
    global GLOBAL_pos

    if arg and ops:
        GLOBAL_commandPath = arg[0]
        arg = arg[1:]
        if isWin:
            arg = _wArgs(arg)

        GLOBAL_args = arg
        GLOBAL_iterMP = miniparse_0(ops, GLOBAL_args)

    while not GLOBAL_iterEnd and GLOBAL_iterMP:
        GLOBAL_pos, turn = next(GLOBAL_iterMP)
        if GLOBAL_pos == -1:
            GLOBAL_iterEnd = True
            return True
            # break

        if separation_mode is Smode.EVERY or \
           separation_mode is Smode.ARG and turn is Turn.OPT or \
           separation_mode is Smode.OPT and turn is Turn.ARG:
            return True
    return False


# -------------------------------------------------------------
# 定義終了
# -------------------------------------------------------------


if __name__ == "__main__":
    separation_mode = Smode.ARG
    usage_mode = Umode.BOTH
    error_code = 1

    pms: TypeOpList = [('', False, 'ファイル名'),
                       ('l', False, '', '詳細情報も表示する'),
                       ('L', True, '階層数', 'Lのコメント'),
                       ('h', False, '', '使い方を表示する'),
                       ('help', False, '', '使い方を表示する'),
                       ('verbose', True, 'ながさ', 'あれの長さ', ),
                       ]
    opp = OpSet(pms)
    miniparse(opp, sys.argv)

    ''' miniparseの呼び出し、ここまで '''

    ''' オプションの取得 '''
    # printOpset(opp)
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
    arglist = get_arguments()
    if arglist:
        print()
        print('コマンド引数リスト = ')
        for arg in arglist:
            print(f'  [{arg}]')

    print()

    ''' HELPメッセージ出力サンプル '''
    if opp.isTrue('h') or opp.isTrue('help'):
        print('このプログラムは、モジュール miniparse の使い方を示すものです。')
        printUsage('', opp, Umode.BOTH)

