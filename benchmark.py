import os
import sys
import math
import time
import glob
import random
import concurrent.futures

def _flash(arr):
  i, contents = arr
  with open('targetssd/%018d.txt'%i, 'w') as f:
    f.write( contents )
  
def flash(mp=1, filenum=10, datasize=10):
  contents = '💓' * (datasize//3) # 雑にUTF8 一文字3bytesとして換算できる
  arr = [(i,contents) for i in range(filenum)]
  with concurrent.futures.ProcessPoolExecutor(max_workers=mp) as executor:
    executor.map( _flash, arr)

def _reads(name):
  with open(name) as f:
    text = f.read()

def reads(mp=1):
  files = glob.glob('targetssd/*') 
  random.shuffle( files )
  _reads( files[0] )
  with concurrent.futures.ProcessPoolExecutor(max_workers=mp) as executor:
    executor.map( _reads, files)

def clean():
  files = glob.glob('targetssd/*')
  [os.remove(file) for file in files]

def main():
  patterns = []
  for mp in [1, 2, 4, 8, 16]:
    for filenum in [1024*10, 1024*10*2, 1024*10*4]: # 10K, 100K, 1000K files
      for datasize in [1000, 10000, 100000]:
        patterns.append( (mp, filenum, datasize) )
  for p in patterns:
    mp, filenum, datasize = p
    start = time.time()
    flash( mp=mp, filenum=filenum, datasize=datasize)
    print('write multiprocess={}, filenum={}, datasize={}(bytes), eplapsed={}'.format(mp, filenum, datasize, time.time() - start) )

    start = time.time()
    reads( mp=mp )
    print('reads multiprocess={}, filenum={}, datasize={}(bytes), eplapsed={}'.format(mp, filenum, datasize, time.time() - start) )
   
    clean()

if __name__ == '__main__':
  main()
