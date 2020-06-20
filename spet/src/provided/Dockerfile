# Usage:
# docker build --build-arg cores=64 --build-arg \
# cflags="-march=znver1 -mtune=znver1" --build-arg \
# url=https://cdn.kernel.org/pub/linux/kernel/v4.x/linux-4.14.4.tar.xz \
# --build-arg version=4.14.4 -t compile_test /path/to/this/file/
#
# docker run --name test1 compile_test
# docker stop test1
# docker rm test1
FROM ubuntu:17.04
ARG cores
ARG cflags
ARG url
ARG version
ENV cores=${cores}
ENV cflags=${cflags}
# Environment Prerequisites
RUN apt-get update && apt-get install -y \
    python3 \
    build-essential \
    gcc \
    bc
# COPY and ADD do not work so we need to download Linux from the URL.
WORKDIR /
ADD ${url} /
RUN tar xf linux-${version}.tar.gz && mv linux-${version} linux
WORKDIR /linux
# setup
RUN make -s -j ${cores} defconfig && make -s -j ${cores} clean
CMD make -s -i -j ${cores} clean; \
ulimit -s unlimited && \
ulimit -n 1048576 && \
python3 -mtimeit -v -n 1 -r 0 -s \
"import subprocess; import os; shell_env = os.environ.copy(); shell_env['CFLAGS'] = '${cflags}'" -v \
"subprocess.check_call('make -s -j ${cores}', shell=True, universal_newlines=True, executable='/bin/bash', env=shell_env)" \
| awk '/raw times:/ {print $3}'
