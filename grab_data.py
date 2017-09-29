#!/usr/bin/env python3

import os
import sys
import urllib
import requests
import gzip
import glob






def download(url, dirpath):
  #download files from ftp server
  filename = url.split('/')[-1]
  if not os.path.exists(dirpath):
      os.makedirs(dirpath)
  filepath = os.path.join(dirpath, filename) #create directory path of the files
  
  u = urllib.request.urlopen(url)
  f = open(filepath, 'wb')
  filesize = int(u.headers["Content-Length"])
  print("Downloading: %s Bytes: %s" % (filename, filesize))

  # create a buffer of size 8192
  downloaded = 0
  block_sz = 8192
  status_width = 70
  while True:
    buf = u.read(block_sz)
    if not buf:
      print('')
      break
    else:
      print('', end='\r')
    downloaded += len(buf)
    f.write(buf)
    status = (("[%-" + str(status_width + 1) + "s] %3.2f%%") %
      ('=' * int(float(downloaded) / filesize * status_width) + '>', downloaded * 100. / filesize))
    print(status, end='')
    sys.stdout.flush()
  f.close()
  return filepath

def is_lunar(year):
  # check the year to see if it is lunar year
    if year%4==0 and year%100 != 0 or year%400 == 0:
        return True
    else:
        return False

def get_date(year, month, day):
  # find this is the nth day in a year
    days = [0, 31,28,31,30, 31,30,31,31,30,31,30,31]
    days_ = 0
    n = int(month)
    for i in range(1, n):
        days_ += days[i]
    days_ += day
    if n > 2 and is_lunar(year):
        days_ += 1
    return days_


def get_url(year, days, sate):
  # creating download url
    url = "ftp://www.ngs.noaa.gov/cors/rinex/"
    url += str(year) + '/'
    d = str(days)
    while len(d) < 3:
        d = '0' + d
    url += d + '/'
    url += sate + '/'
    url += sate + str(days) + '0.'
    url += str(year)[2:] + 'o.gz'
    return url


def un_gz(filename):
  # unzip .gz files
    
    f_name = filename.replace(".gz", "")   
    g_file = gzip.GzipFile(filename)  
    open(f_name, "wb+").write(g_file.read())  
    g_file.close()  



if __name__ == '__main__':

  # check arguments
    args = sys.argv
    if len(args) != 4:
        print('Not correct command. ex: ./grab_data sate timestamp1 timestamp2')
        sys.exit()
    sate = args[1]
    ts1 = args[2]
    ts2 = args[3]

  # check start and end date
    year1 = int(ts1.split('-')[0])
    year2 = int(ts2.split('-')[0])
    

    month1 = int(ts1.split('-')[1])
    date1 = int(ts1.split('-')[2][:2])
    month2 = int(ts2.split('-')[1])
    date2 = int(ts2.split('-')[2][:2])
    start_day = get_date(year1, month1, date1)
    end_day = get_date(year2, month2, date2)

    cur_year = year1
    
    while cur_year <= year2:
        if is_lunar(cur_year):
            n= 366
        else:
            n = 365
        if cur_year == year1:
            sd = start_day
        else:
            sd = 1
        if cur_year == year2:
            ed = end_day
        else:
            ed = n
        for d in range(sd, ed + 1):
            url = get_url(cur_year, d, sate )
            print('downloading...')
            print(url)
            try:
              download(url, 'example/')
            except:
                print('no such file')
        cur_year += 1
    
    #End of downloading
    dir = os.path.dirname(__file__)
    filelist = glob.glob(os.path.join(dir,'example/*'))
    for f in filelist:
        if f.endswith('.gz'):
            print('unzipping...')
            print(f)
            un_gz(f)

    
    #End of extracting
    dir = os.path.dirname(__file__)
    filelist = glob.glob(os.path.join(dir,'example/*'))
    params = []
    for f in filelist:
        if f.endswith('o'):
            params.append(f)

    command = './teqc '
    for p in params:
        command += p + ' '
    command += '> '
    command += sate + '.obs'

    print('Merging...')
    os.system(command)
    
    











