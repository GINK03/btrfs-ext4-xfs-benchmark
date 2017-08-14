import os
import sys


# ファイルを作りまくって問題がない限界を確認する
count = 0
while True:
  count += 1
  if count % 10000 == 0:
    print('now iter', count)
  try: 
    open('targetssd/{}'.format(count), 'w' )
  except Exception as e:
    print( e )
    print( 'max file number is', count )
    break
  
