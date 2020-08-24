import sys
import miniparse as mp

ops = {'a': mp.Oset(False, False, 'comment for a'),
       'L': mp.Oset(False, True, 'Lのコメント'),
       'f': mp.Oset(False, False, 'これがfです'),
       'l': mp.Oset(False, False, 'これがlです'),
       'verbose': mp.Oset(False, True, '静かにね'),
       }

mp.printpms(ops)

mp.miniparse(sys.argv[1:], ops)

mp.printpms(ops)

if ops['l'].isTrue:
    print('オプション <l> はあり')
else:
    print('オプション <l> はなし')
