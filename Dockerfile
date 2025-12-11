# Build Stage
FROM ubuntu:20.04 as builder
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y cmake g++ wget

WORKDIR /build
COPY . .
# 只需要 httplib.h
RUN wget https://raw.githubusercontent.com/yhirose/cpp-httplib/master/httplib.h -O src/httplib.h
RUN mkdir build && cd build && cmake .. && make

# Run Stage
FROM ubuntu:20.04
WORKDIR /app
# 复制编译好的程序
COPY --from=builder /build/build/server /app/server
# 复制静态资源
COPY static /app/static
# 确保数据目录存在
RUN mkdir -p /app/data

EXPOSE 8080
CMD ["./server"]