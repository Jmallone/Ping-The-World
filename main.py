import random
import traceback
import subprocess
import time
import os

from multiprocessing.pool import ThreadPool, Pool

FNULL = open(os.devnull, 'w')

def get_random_ip():
    return '.'.join(map(str, [random.randint(0, 255) for i in range(4)]))

def ping_ip(ip, lat, lon):
    try:
        print(ip, lat, lon, '?')
        t0 = time.time()
        status = subprocess.call(['ping', '-c1', '-t25', ip], stdout=FNULL, stderr=FNULL)
        print(status)
        if status != 0:
            return None
        return ip, lat, lon, time.time() - t0
    except:
        traceback.print_exc()

if __name__ == '__main__':
    pool = ThreadPool(processes=100)
    f = open('log.txt', 'a')

    def cb(result):
        print(result)
        if result is None:
            return
        ip, lat, lon, t = result
        print(lat, lon, t, file=f)

    from geolite2 import geolite2
    reader = geolite2.reader()

    for i in range(10000):
        ip = get_random_ip()
        match = reader.get(ip)
        # print(match)
        if match is None or not ('location' in match.keys()):
            continue
        lat, lon = match['location']['latitude'], match['location']['longitude']
        pool.apply_async(ping_ip, args=(ip, lat, lon), callback=cb)

    pool.close()
    pool.join()

    f.close()
