# 在后台运行构建
build-wiki:
	nohup python wiki-service/build.py &
	rm nohup.out

# 获取进程号
build-ps:
	ps aux | grep 'python wiki-service/build.py'

build-log:
	tail -f /proc/863482/fd/1
