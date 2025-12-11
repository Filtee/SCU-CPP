#!/bin/bash
set -e

# 进入数据目录
cd /app/data

echo "Checking dataset files..."

# 遍历所有 .gz 文件
for f in *.gz; do
    # 获取解压后的文件名 (去掉 .gz 后缀)
    # 例如: train-images-idx3-ubyte.gz -> train-images-idx3-ubyte
    filename="${f%.*}"
    
    # 如果解压后的文件不存在，则解压
    if [ ! -f "$filename" ]; then
        echo "--> Unzipping $f..."
        # -k: 保留源文件, -d: 解压
        gzip -k -d "$f"
    else
        echo "--> $filename already exists, skipping."
    fi
done

# 回到工作目录
cd /app

# 执行 Docker CMD 传入的命令 (即启动 server)
echo "Starting Neural Network Server..."
exec "$@"