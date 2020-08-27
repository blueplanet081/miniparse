from typing import List, Dict
import sys

if sys.version_info < (3, 8):
    print('このモジュールは、Python 3.8以降に対応しています。ごめんなさい。')
    print('もし、モジュール内の <:=> 演算子部分を2行に書き換えれば、3.7以前でも動くかもしれません。')
    sys.exit()


class Oset():
    def __init__(self, isTrue: bool, needParam: bool, comment: str = ''):
        ''' コマンドラインオプション情報を格納するclass
        '''
        self.isTrue = isTrue
        self.needParam = needParam
        self.param = ''
        self.comment = comment


def printpms(pm: Dict[str, 'Oset']) -> None:
    for pp in pm:
        print(pp, pm[pp].isTrue, pm[pp].param, pm[pp].comment)


class Args():
    ''' コマンドラインオプション解析用class
    '''
    def __init__(self, args: List[str]):
        self.__args = args
        self.__num = 0
        self.__pos = 0

    def transNext(self) -> bool:
        ''' 次の引数ブロックに移行する。
            途中でも強制的に次に移行するので注意。
            次が無かったらFalseを返す
        '''
        self.__num += 1
        self.__pos = 0
        return self.__num < len(self.__args)

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
        return self.__args[self.__num:]


__params = []


def params() -> List[str]:
    return __params


def miniparse(argv: List[str], pms: Dict[str, 'Oset'], mode: int = 0) -> List[str]:
    # tm = Args(sys.argv[1:])
    tm = Args(argv)
    while not tm.isAllEnd():
        if tm.optionType() == '-':      # シングルオプションブロック
            while p := tm.getOne():
                # print(p)
                if p in pms:
                    pms[p].isTrue = True
                    if pms[p].needParam:    # オプションパラメータ必要
                        if op := tm.getAll():
                            pms[p].param = op
                        elif op := tm.getOpParam():
                            pms[p].param = op
                        else:
                            print(f"missing option parameter of '{p}'")
                        break
                else:
                    print(f"unknown option '{p}'")
                    tm.getAll()     # エラーなので、ブロックの残りを空読み
                    break
        elif tm.optionType() == '--' and (p := tm.getLong()):   # ロングオプションブロック
            if p in pms:
                pms[p].isTrue = True
                if op := tm.getAll():       # '=xxxx' が付いてた
                    pms[p].param = op
                elif pms[p].needParam:      # オプションパラメータ必要
                    pms[p].param = tm.getOpParam()
            else:
                print(f"unknown option '{p}'")
        else:                           # コマンドパラメータブロック
            if tm.isEndBlock():         # 多分前のブロックが '--' だった
                tm.transNext()
            param = tm.getAll()
            __params.append(param)
            if mode != 0:
                if tm.transNext():
                    return tm.remainArgs()
                else:
                    return []

        if tm.isEndBlock():
            tm.transNext()

    return []


if __name__ == "__main__":

    pm = {'a': Oset(False, False, 'comment for a'),
          'L': Oset(False, True, 'Lのコメント'),
          'f': Oset(False, False, 'これがfです'),
          'l': Oset(False, False, 'これがlです'),
          'verbose': Oset(False, True, '静かにね'),
          }

    printpms(pm)
    print('----')

    ret = miniparse(sys.argv[1:], pm, 1)
    print('----')
    print(ret)
    printpms(pm)

    ret = miniparse(ret, pm, 1)
    print('----')
    print(ret)
    printpms(pm)

    ret = miniparse(ret, pm, 1)
    print('----')
    print(ret)
    printpms(pm)

    for i, p in enumerate(params()):
        print(i, p)

    if pm['l'].isTrue:
        print('オプション <l> はあり')
    else:
        print('オプション <l> はなし')
