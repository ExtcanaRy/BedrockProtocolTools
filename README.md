# ***本工具包所有内容基于GPL3.0开源，请勿将本项目用于非法用途***
# 使用`git clone https://github.com/WillowSauceR/tools`将本项目克隆到本地或直接下载本项目，然后使用python3来运行
## scan.py
### usage: `python3 scan.py [IP]`
#### description: 扫描一个IP上的所有BE协议服务器，使用前建议安装[Npcap](https://npcap.com/dist/npcap-1.60.exe)，然后使用命令`pip install scapy`来安装依赖，基于scapy，基本不漏服

## send.py 
### usage: `python3 send.py [IP] [端口] [载体包文件] [次数] [间隔:秒]`
#### description: 发包复现工具, 需要一个内含byte数据的文件，一般为.dmp后缀名

## motd.py
### usage: `python3 motd.py [IP] [端口]`
#### description: motd一个BE服务器，支持自动解析返回的数据

## scanall.py
### usage: `python3 scanall`
#### description: 扫描全网端口为19132的服，需要配合[wireshark](https://mirrors.tuna.tsinghua.edu.cn/wireshark/win64/Wireshark-win64-3.6.2.exe)抓取返回包
##### wireshark参数:
##### 捕获过滤器: `not src host 你的局域网IP and udp and port 19132`
##### 显示过滤器: `udp.length > 75 && ip.src == 0.0.0.0/0`