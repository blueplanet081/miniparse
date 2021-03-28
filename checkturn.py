from enum import Enum, auto
from typing import Optional

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

a = CheckTurn()
print(a.checkTurn(), str(a.getTurn()))
print(a.checkTurn(Turn.OPT), str(a.getTurn()))
print(a.checkTurn(Turn.OPT), str(a.getTurn()))
print(a.checkTurn(Turn.ARG), str(a.getTurn()))
print(a.checkTurn(Turn.ARG), str(a.getTurn()))
print(a.checkTurn(Turn.ARG), str(a.getTurn()))
print(a.checkTurn(Turn.OPT), str(a.getTurn()))
print(a.checkTurn(Turn.ARG), str(a.getTurn()))

    # def checkTurnx(self, turn: Optional[Enum] = None) -> bool:
    #     ''' ターンの状態をチェックする。前回のターンから変わったら True
    #     '''
    #     if turn:                        # 省略時は現在のチェック状態を返す
    #         if turn is self.__turn:     # 前回と同じ(False)
    #             self.__turncheck = False
    #         else:                       # ターン！（True だが、初回は False）
    #             self.__turncheck = True if self.__turn else False
    #             self.__turn = turn
    #     return self.__turncheck

