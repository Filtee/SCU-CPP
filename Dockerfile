# Build Stage
FROM ubuntu:20.04 as builder
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y cmake g++ wget

WORKDIR /build
COPY . .
RUN wget https://raw.githubusercontent.com/yhirose/cpp-httplib/master/httplib.h -O src/httplib.h
RUN mkdir build && cd build && cmake .. && make

# Run Stage
FROM ubuntu:20.04
ENV DEBIAN_FRONTEND=noninteractive

# 安装 gzip 用于解压数据
RUN apt-get update && apt-get install -y gzip && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 复制编译产物
COPY --from=builder /build/build/server /app/server
COPY static /app/static
# 复制启动脚本
COPY entrypoint.sh /app/entrypoint.sh

# 确保脚本有执行权限
RUN chmod +x /app/entrypoint.sh

# 确保数据目录存在
RUN mkdir -p /app/data

EXPOSE 8080

# 【修改点 3】设置 Entrypoint 为我们的脚本
ENTRYPOINT ["/app/entrypoint.sh"]

# 默认命令
CMD ["./server"]