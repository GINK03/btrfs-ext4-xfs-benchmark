# Filesystem Benchmark

## 各ファイルシステムで数多くのフィイルを作るような用途で最もパフォーマンスが良いものはどれか
検討します


## 背景：btrfsのサポートがRHELで断念される
[マイナビニュース](http://news.mynavi.jp/news/2017/08/04/056/)にこのような文章が発表されました  

> Btrfsは長年にわたって作業をしているにもかかわらず、依然として技術的な問題が存在しており今後も改善が期待しにくいこと、ZFSはライセンスの関係で取り込むことができないこと、既存の技術と継続しながら新技術を実現するという観点から、当面はXFSをベースとしつつ機能拡張を進めていく「Stratis」プロジェクトを進めることが妥当ではないかと提案している。

しかし、[ArchWik](https://wiki.archlinuxjp.org/index.php/Btrfs)には、このようにもあり、btrfsの今後がどうなるかよくわからないです  
> Btrfs またの名を "Better FS" — Btrfs は新しいファイルシステムで Sun/Oracle の ZFS に似たパワフルな機能を備えています。機能としては、スナップショット、マルチディスク・ストライピング、ミラーリング (mdadm を使わないソフトウェア RAID)、チェックサム、増分バックアップ、容量の節約だけでなく優れたパフォーマンスも得られる透過圧縮などがあります。現在 Btrfs はメインラインカーネルにマージされており安定していると考えられています [1]。将来的に Btrfs は全てのメジャーなディストリビューションのインストーラで標準になる GNU/Linux ファイルシステム として期待されています。

Linuxで使えるファイルシステムは多岐に渡りますが、何が最も良いのでしょうか。 

ビッグデータの用途で、File Systemを用いたKVSか、LevelDBなどのKVSを用いることがよくあり、この用途では細かい数キロから数メガのファイルを大量に作ります  
そのため、数多くのinodeを持つことができるbtrfsを今まで用いて来たのですが、他のファイルシステムも検討することにします  

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

ext4はそのファイルシステムの制約で、最初にmkfs.ext4した時にinodeの最大値を決めるんですが、ちょくちょくデフォルトから超えてしまい、分析が途中で破綻してしまい、苦しい目をみることになることが多いです　　　


## format parameters
フォーマットには可能なかぎり、オプションは指定しません  
つまりデフォルトで用いたらどういう場合にパフォーマンスが高いかという視点です  
```console:f2fs
F2FS-tools: mkfs.f2fs Ver: 1.8.0 (2017-02-03)
Info: Debug level = 0
Info: Label = 
Info: Trim is enabled
Info: [/dev/sdd] Disk Model: SanDisk SDSSDA4830RL
Info: Segments per section = 1
Info: Sections per zone = 1
Info: sector size = 512
Info: total sectors = 937703088 (457862 MB)
Info: zone aligned segment0 blkaddr: 512
Info: format version with
  "Linux version 4.12.5-1-ARCH (builduser@tobias) (gcc version 7.1.1 20170630 (GCC) ) #1 SMP PREEMPT Fri Aug 11 12:40:21 CEST 2017"
Info: [/dev/sdd] Discarding device
Info: This device doesn't support BLKSECDISCARD
```

## パフォーマンステスト
シーケンシャルな大きなファイルの読み書きは今回はみません  
KVS的に使う用途を考えており、数キロから数メガのファイルをとにかく大量に作ることを目的とします　　



  <img width="750px" src="https://user-images.githubusercontent.com/4949982/29271950-e431e980-8138-11e7-9f4c-a569ba38a3f4.png">sh
  <img width="750px" src="https://user-images.githubusercontent.com/4949982/29271950-e431e980-8138-11e7-9f4c-a569ba38a3f4.png">
