from miniparse import PARTIAL
from typing import Union, List, Dict, Tuple


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



pm = {'a': Oset(False, False, '', 'comment for a'),
      'L': Oset(False, True, '<階層数>', 'Lのコメント'),
      'f': Oset(False, False, '', 'これがfです'),
      'l': Oset(False, False, '', 'これがlです'),
      'verbose': Oset(False, False, '<引数（省略時はアレ）>', '静かにね'),
      }


def make_usage(dpm: Dict[str, 'Oset']) -> str:
    pstr = 'usage:'
    if pp1 := [pp for pp in pm if len(pp) == 1 and not pm[pp].needArg]:
        pstr += ' -'
        for p in pp1:
            pstr += p
    if pp1 := [pp for pp in pm if len(pp) == 1 and pm[pp].needArg]:
        for p in pp1:
            pstr += f' -{p} {pm[p].Argcomment}'
    if pp1 := [pp for pp in pm if len(pp) > 1]:
        for p in pp1:
            pstr += f' --{p}'
            if pm[p].Argcomment:
                pstr += f'={pm[p].Argcomment}'


    print(pstr)
    for pp in pm:
        if len(pp) == 1:
            if pm[pp].needArg:
                print('    -{0} {1}: {2}'.format(pp, pm[pp].Argcomment, pm[pp].comment))
            else:
                print('    -{0}: {1}'.format(pp, pm[pp].comment))
        else:
            if pm[pp].Argcomment != '':
                print('    --{0}={1}: {2}'.format(pp, pm[pp].Argcomment, pm[pp].comment))
            else:
                print('    --{0}: {1}'.format(pp, pm[pp].comment))



make_usage(pm)