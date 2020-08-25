import sys
import miniparse as mp

ops = {'a': mp.Oset(False, False, 'comment for a'),
       'L': mp.Oset(False, True, 'Lのコメント'),
       'f': mp.Oset(False, False, 'これがfです'),
       'l': mp.Oset(False, False, 'これがlです'),
       'verbose': mp.Oset(False, True, '静かにね'),
       }

mp.printOset(ops)


myArgs = mp.Args(sys.argv[1:])
mp.miniparse(myArgs, ops, 1)

mp.printOset(ops)
print(myArgs.remainArgs())

for i, p in enumerate(mp.params()):
    print(i, p)

if ops['l'].isTrue:
    print('オプション <l> はあり')
else:
    print('オプション <l> はなし')
