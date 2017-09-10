# Filesystem Benchmark For Map Reduce

## 多コアCPU, GPUなどの発展により、一台のマシンで効率的なmap reduceができるようになりました
Map Reduceはそのアルゴルズムから分散性能が十分な際、複数のマシンで分割してタスクを実行できるので、ビッグデータを処理する際には非常に便利なのですが、これはnVidia社のCUDAやAMD　Ryzenなどの極めてコア数が多いCPUなどと、高速なIOをもつDiskであるNVMeなども用いることで、同様のシステムを一台のコンピュータで完結させることができるようになりました。  

会社ではAWSのElastic Map Reduceを使うほどの分析じゃないけど、コストを安く、定常的にMap Reduceで処理したいというモチベーションの時、自作したMap Reduceフレームワークを使っています  

と言っても、優秀なファイルシステム、高速なディスクIO、マルチコアの強力な並列性に依存しており、まさに巨人の肩の上に立つと言った感じです。  

## 自作したMapReduceシステム概要

Mapperの出力を、オンメモリで保持するのではなく、NVMeに直接かきこむことで、Reducerが特定のキーの粒度で集められたデータを処理することができます。オンメモリでデータを保持しないことで、ディスクの容量とディスクのファイルシステムが許す限り、書き込むことができるので、この限界値を考えなければ、どんなに大きいデータであっても、それなりの時間で処理することができます。（データの特徴や粒度によっては大規模クラスタリングしたHadoopより早いです）  

<p align="center">
  <img width="600px" src="https://user-images.githubusercontent.com/4949982/30248513-fd2d06f0-9663-11e7-9197-ec1a9587256e.png">
</p>
<div align="center"> 図1. 作成したコンピュータ一台で動作するMap Reduce(Mapperの出力先はbtrfsでフォーマットしたNVMe) </div>

## 課題：btrfの開発がRHELで断念される
[マイナビニュース](http://news.mynavi.jp/news/2017/08/04/056/)にこのような文章が発表されました  

> Btrfsは長年にわたって作業をしているにもかかわらず、依然として技術的な問題が存在しており今後も改善が期待しにくいこと、ZFSはライセンスの関係で取り込むことができないこと、既存の技術と継続しながら新技術を実現するという観点から、当面はXFSをベースとしつつ機能拡張を進めていく「Stratis」プロジェクトを進めることが妥当ではないかと提案している。

しかし、[ArchWik](https://wiki.archlinuxjp.org/index.php/Btrfs)には、このようにもあり、btrfsの今後がどうなるかよくわからないです  
> Btrfs またの名を "Better FS" — Btrfs は新しいファイルシステムで Sun/Oracle の ZFS に似たパワフルな機能を備えています。機能としては、スナップショット、マルチディスク・ストライピング、ミラーリング (mdadm を使わないソフトウェア RAID)、チェックサム、増分バックアップ、容量の節約だけでなく優れたパフォーマンスも得られる透過圧縮などがあります。現在 Btrfs はメインラインカーネルにマージされており安定していると考えられています [1]。将来的に Btrfs は全てのメジャーなディストリビューションのインストーラで標準になる GNU/Linux ファイルシステム として期待されています。

まじか。引っ越しの検討だけはつけておかなきゃ！  

Linuxで使えるファイルシステムは多岐に渡りますが、今回の用途では、何が最も良いのでしょうか。 

ビッグデータの用途で、ファイルシステムをKVSのように用いたり、LevelDBなどのKVSを用いることがよくあり、この用途では細かい数キロから数メガのファイルを大量に作ります  

そのため、数多くのファイルを持つことができ、パフォーマンスが高いbtrfsを今まで用いてきたのですが、他のファイルシステムも検討することにします  

## 検討対象のファイルシステムとその実験環境
まず、条件を整えるため、ハードウェアは固定します
- CPU: RYZEN7 1700X
- Memory: 36GByte DDR4
- HDD1: SanDisk SSD UltraII 480GB (OS起動用)
- HDD2: インテル SSD 600pシリーズ 512GB M.2 PCIEx4（検証用）

OSとそのバージョン
- ArchLinux 4.12.4-1-ARCH (x86_64)

検証対象ファイルシステム
- ext4
- btrfs
- xfs
- ntfs
- f2fs
- jfs
- reiserfs

zfsに関しては、この時、ソフトウェアがこのバージョンのカーネル用にコンパイル & インストールできなかったので、諦めました

実験で読み書きするデータ
- map reduceでよくあるパターンのファイルを作り出す[スクリプト](https://github.com/GINK03/btrfs-micro-mapreduce-benchmark/)で実験を行います（1〜16プロセスで可変させて、大量のファイルの読み書きを行います）

## 各種ファイルシステム最大容量、最大ファイル数
ext4はそのファイルシステムの制約で、最初にmkfs.ext4した時にinodeの最大値を決めるのですが、ちょくちょくデフォルトから超えてしまい、分析が途中で破綻してしまい、苦しい目をみることになることが多いです　　　

他のファイルシステムは、サイズ、ファイル数はどうなっているのでしょうか  

<p align="center">
  <img width="100%" src="https://user-images.githubusercontent.com/4949982/29271950-e431e980-8138-11e7-9f4c-a569ba38a3f4.png">
</p>

## format parameters
フォーマットには可能なかぎり、オプションは指定しません  
つまりデフォルトで用いたらどういう場合にパフォーマンスが高いかという視点です  
```console: each version
mkfs.f2fs: mkfs.f2fs Ver: 1.8.0 (2017-02-03)
mkfs.ext4: mke2fs 1.43.5 (04-Aug-2017)
mkfs.ntfs: mkntfs v2017.3.23 (libntfs-3g)
mkfs.btrfs: mkfs.btrfs, part of btrfs-progs v4.12
mkfs.jfs: mkfs.jfs version 1.1.15, 04-Mar-2011
mkfs.reiserfs: (バージョンコマンドでなぜか何も表示されない。。。)
mkfs.xfs: mkfs.xfs version 4.12.0
```

## パフォーマンステスト
シーケンシャルで大きなファイルの読み書きは今回は考慮しません  

ビッグデータ分析などに使う用途を考えており、数キロから数メガのファイルをとにかく大量に作り、読み書くことを目的とします　　

今回、よく使う方法で並列アクセスをするベンチマーク用のスクリプトを作成したので、それでみていくことにします　　
```console
$ python3 benchmark.py | tee log.txt
```
あるあるなパターンを作り出して、ファイルを読み書きをして、どの程度で終わるかを検証します  

1K, 10K, 100Kバイトのファイルをそれぞれ、10000, 20000, 40000個作成するのに、どの程度の時間が必要かを測定します  

また、作成したファイルを読み取るのにどの程度必要なのかを測定します  

## 結果
<p align="center">
  <img width="650px" src="https://user-images.githubusercontent.com/4949982/29276439-9c5c2c72-8149-11e7-9ba4-5229ed9579ea.png">
</p>
<div align="center">  図1. ext4 format </div>

<p align="center">
  <img width="650px" src="https://user-images.githubusercontent.com/4949982/29276461-af87b816-8149-11e7-902d-de4196c5dd3a.png">
</p>
<div align="center">  図2. btrfs format </div>

<p align="center">
  <img width="650px" src="https://user-images.githubusercontent.com/4949982/29276473-b7641278-8149-11e7-9af7-43bf62770757.png">
</p>
<div align="center">  図3. f2fs format </div>

<p align="center">
  <img width="650px" src="https://user-images.githubusercontent.com/4949982/29276489-c09b3434-8149-11e7-87f4-2104ec614961.png">
</p>
<div align="center">  図4. reiserfs format </div>

<p align="center">
  <img width="650px" src="https://user-images.githubusercontent.com/4949982/29276507-cad7398e-8149-11e7-88f1-678bab06804f.png">
</p>
<div align="center">  図5. ntfs format(オレンジが場外に飛んだ) </div>

<p align="center">
  <img width="650px" src="https://user-images.githubusercontent.com/4949982/29276516-d28560d4-8149-11e7-9d42-cc589d7badd4.png">
</p>
<div align="center">  図６. xfs format </div>

<p align="center">
  <img width="650px" src="https://user-images.githubusercontent.com/4949982/29276534-de646990-8149-11e7-808b-8df75f7d351b.png">
</p>
<div align="center">  図7. jfs format </div>

<p align="center">
  <img width="650px" src="https://user-images.githubusercontent.com/4949982/29276555-eaafcda2-8149-11e7-92d6-b9cc639551d7.png">
</p>
<div align="center">  図8. ext4 format @ ラズベリーパイ class 10 U3（オマケ） </div>

### ext4を基準とした時のパフォーマンス
ext4のパフォーマンスを1とした時に、相対的にどの程度の速さ（小さい方がいい）なのかを表示します
<p align="center">
  <img width="100%" src="https://user-images.githubusercontent.com/4949982/29281711-0b238586-815b-11e7-81a2-70f26cfac4f9.png">
</p>
<div align="center">  図9. ext4からの相対的な速度 </div>


## f2fs max file number challenge
F2FSがこのわたしが分析でよく用いるデザインパターンにおいて最もパフォーマンスが良いことがわかりました。  

ドキュメントやWikiをさらっても、F2FSの最大ファイルサイズがよくわからないのですが、もともとこのファイルシステムが作られた背景である、フラッシュメモリを効率的に長寿命にもちいたいというモチベーションから考えると、armhf（32bit Armアーキテクチャ）をサポートしたいはずなので、2^32個までいけるんじゃないでしょうか  

ext4では500万個を超える程度のファイルを作ると、もう、デフォルトではinodeが埋まってしまい、書き込めないです  

直近では4000万個ほどの、ファイルを用いる必要があり、とりあえずこの個数までファイルを作れれば良さそうです  
```python:disaster.py
# ファイルを作りまくって問題がない限界を確認する
count = 0
for i in range(40000000):
  count += 1
  if count % 10000 == 0:
    print('now iter', count)
  try: 
    open('targetssd/{}'.format(count), 'w' )
  except Exception as e:
    print( e )
    print( 'max file number is', count )
    break
```
以下のコマンドを実行したところ、問題なく完了することができました  
```console
$ time python3 make_disaster.py
```

## 参考：オフィシャルサイトでのベンチマーク  
[公式サイトで様々な角度からのベンチマーク](https://jaegeuk.github.io/perf_results/phoronix/05_08_2017/merge-9898/index.html)が行われました 
nvme, randiskやssdなどで様々な角度からベンチマークが行われています  
やはりというかなんというか、新しいフォーマットで新しい規格のほど、スコアが良いように見えます

## まとめ
全く注目していなかったF2FSが思いの外良いパフォーマンスを出したので、アドホックな集計や分析の選択肢に加えるのはありだと思います。  

今後もbtrfsの開発は続いて行くと考えられますが、RHELの影響でどう転ぶかわからないので、長期的に使うシステムには安全策としてXFSなど古くからあって数多くのファイル数を扱え、パフォーマンスが良い、フォーマットも良いと思います  
