# Filesystem Benchmark

## 各ファイルシステムで数多くのフィイルを作るような用途で最もパフォーマンスが良いものはどれか
検討します


## 背景：btrfsがRHELで断念される
[マイナビニュース](http://news.mynavi.jp/news/2017/08/04/056/)にこのような文章が発表されました  

> Btrfsは長年にわたって作業をしているにもかかわらず、依然として技術的な問題が存在しており今後も改善が期待しにくいこと、ZFSはライセンスの関係で取り込むことができないこと、既存の技術と継続しながら新技術を実現するという観点から、当面はXFSをベースとしつつ機能拡張を進めていく「Stratis」プロジェクトを進めることが妥当ではないかと提案している。

しかし、[ArchWik](https://wiki.archlinuxjp.org/index.php/Btrfs)には、このようにもあり、btrfsの今後がどうなるかよくわからないです  
> Btrfs またの名を "Better FS" — Btrfs は新しいファイルシステムで Sun/Oracle の ZFS に似たパワフルな機能を備えています。機能としては、スナップショット、マルチディスク・ストライピング、ミラーリング (mdadm を使わないソフトウェア RAID)、チェックサム、増分バックアップ、容量の節約だけでなく優れたパフォーマンスも得られる透過圧縮などがあります。現在 Btrfs はメインラインカーネルにマージされており安定していると考えられています [1]。将来的に Btrfs は全てのメジャーなディストリビューションのインストーラで標準になる GNU/Linux ファイルシステム として期待されています。

Linuxで使えるファイルシステムは多岐に渡りますが、何が最も良いのでしょうか。 

ビッグデータの用途で、File SystemをKVSのように用いたり、LevelDBなどのKVSを用いることがよくあり、この用途では細かい数キロから数メガのファイルを大量に作ります  
そのため、数多くのファイルを持つことができるbtrfsを今まで用いてきたのですが、他のファイルシステムも検討することにします  

## 検討対象のファイルシステムとその実験環境
まず、条件を整えるため、ハードウェアは固定します
- CPU: RYZEN7 1700X
- Memory: 36GByte DDR4
- HDD1: インテル SSD 600pシリーズ 512GB M.2 PCIEx4 (OS起動用)
- HDD2: SanDisk SSD UltraII 480GB（検証用）

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

## 各種ファイルシステム最大容量、最大ファイル数
ext4以外を私が積極的に使うことが多い理由の一つとして、ext4の最大ファイル数を超える分析が多いからです  

他のファイルシステムは、サイズ、ファイル数はどうなっているのでしょうか
<p align="center">
  <img width="750px" src="https://user-images.githubusercontent.com/4949982/29271950-e431e980-8138-11e7-9f4c-a569ba38a3f4.png">
</p>

ext4はそのファイルシステムの制約で、最初にmkfs.ext4した時にinodeの最大値を決めるのですが、ちょくちょくデフォルトから超えてしまい、分析が途中で破綻してしまい、苦しい目をみることになることが多いです　　　


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
シーケンシャルな大きなファイルの読み書きは今回は考慮しません  
KVS的に使う用途を考えており、数キロから数メガのファイルをとにかく大量に作ることを目的とします　　

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

## f2fs max file number challenge
F2FSがこのわたしが分析でよく用いるデザインパターンにおいて最もパフォーマンスが良いことがわかりました。  

ドキュメントやWikiをさらっても、F2FSの最大ファイルサイズがよくわからないのですが、もともとこのファイルシステムが作られた背景である、フラッシュメモリを効率的に長寿命にもちいたいというモチベーションから考えると、armhf（32bit Armアーキテクチャ）もサポートしたいはずなので、2^32個までいけるんじゃないでしょうか  

ext4では500万個を超える程度のファイルを作ると、もう、デフォルトではinodeが埋まってしまい、書き込めないです  

直近では4000万個ほどの、ファイルを用いる必要があり、とりあえずこの個数までファイルを作れれば良さそうです  
```python:disaster.py
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
```
