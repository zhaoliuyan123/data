import time


def text(user=None, state=None):
    T = time.strftime("%Y-%m-%d %H:%M:%S")
    pat = 'text/{}.txt'.format(time.strftime("%Y-%m-%d"))
    f = open(pat, 'a', encoding='utf-8')
    f.write(T + '  ')
    f.write(str(user) + '  ' + str(state))
    f.write('\n')
    f.close()