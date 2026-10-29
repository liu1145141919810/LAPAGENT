ssh -N -L 6379:127.0.0.1:6379 ceg@172.17.21.20
#建立本地redis端口到远端redis端口的映射
#必须先进入配置server于wsl中