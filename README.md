# graces: Gragh Cut Chinese Segment Tool 基于图割的无监督中文分词器

## 介绍

## 安装

### 通过github安装

### 通过PyPi安装

## 快速开始

### 使用命令行交互
```python
python -m graces -s 饮食可，睡眠可，大便不规律，小便正常，体重无明显减轻。
python -m graces -f ./input.txt -o ./output.txt
```

### 在python中import
```python
import graces
graces.cut("饮食可，睡眠可，大便不规律，小便正常，体重无明显减轻。") # 对单句分词
graces.cut_k("饮食可，睡眠可，大便不规律，小便正常，体重无明显减轻。", k=8) # 对单句分词，指定词数
graces.cut_file("./input.txt", "./output.txt") # 对文件分词
```

## 获取模型

### 下载模型

### 利用自己的语料库生成模型

## 模型表现

### 准确性

### 分词速度

## 贡献者

