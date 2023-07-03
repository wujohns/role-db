# 在后台运行构建
build-wiki:
	nohup python wiki-mongo/quick_build.py > logs/build.log 2>&1 &

# 获取进程号
build-ps:
	ps aux | grep 'python wiki-mongo/quick_build.py'

build-log:
	tail -f /proc/863482/fd/1

# 启动 role-service
role-dev:
	python role-service/app.py

pm2-start:
	pm2 start pm2.config.js
