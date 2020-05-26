# import datetime
# times = datetime.datetime.now() + datetime.timedelta(days=5)
# print(times)
# import re
# files = ['a', 'b', 'c', 'd']
# for url in files:
#     if type(url) == str:
#         txt_str = url.decode().strip()
#         url = re.sub(r'[,|，]', '', txt_str)
#         if 'http' not in url or len(url) > 100 or len(url) < 1:
#             continue
#     else:
#         print(url)
# f = open('a.txt','a')
# for x in range(1,20):
#     f.write(str(x))
# f.close()
import time
import re

a = 'http://data.zz.baidu.com/?appid=16575e762czc0add6&1646555555'
print(re.findall('appid=(.*?)&', a))
data_time = time.strftime("%Y-%m-%d")
print(data_time)
