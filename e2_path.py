from pathlib import Path
from datetime import datetime

"""
o2_path モジュール（添付用短縮版．．ホントはもっとすごいのよ）
os.path とか pathlib を補完する私的モジュール
2020年5月
"""


def is_HiddenName(entry: Path) -> bool:
    ''' 隠しファイルまたはディレクトリ（'.' で始まるname）かどうかを判断する
    '''
    return entry.name.startswith('.')


def is_SystemName(entry: Path) -> bool:
    ''' システムファイルまたはディレクトリ（'__name__'）かどうかを判断する
    '''
    name = entry.name
    return len(name) > 4 and name.startswith('__') and name.endswith('__')


def get_fileSize(entry: Path) -> int:
    ''' ファイルサイズを取得する
    '''
    return entry.stat().st_size


# --------------------------------------------------
# オペレーティングシステムから返される"ctime"
# Windowsでは作成時刻
# --------------------------------------------------

def get_dtctime(entry: Path) -> datetime:
    ''' オペレーティングシステムから返される＜ctime＞を、datetimeオブジェクトで返す
        ＜ctime＞は、Windowsでは作成日時
    '''
    return datetime.fromtimestamp(entry.stat().st_ctime)
    # return datetime.fromtimestamp(os.path.getctime(entry))


def get_dtatime(entry: Path) -> datetime:
    ''' オペレーティングシステムから返される＜atime＞（最終アクセス日時）を、
        datetimeオブジェクトで返す。
        ＜atime＞は、Windowsではわけのわからない日時（mtimeと同じ？）
    '''
    return datetime.fromtimestamp(entry.stat().st_atime)


def get_dtmtime(entry: Path) -> datetime:
    ''' オペレーティングシステムから返される＜mtime＞（最終変更日時）を、
        datetimeオブジェクトで返す。
        ＜mtime＞は、Windowsでの<タイムスタンプ>
    '''
    return datetime.fromtimestamp(entry.stat().st_mtime)

