# ***本工具包所有内容基于GPL3.0开源，请勿将本项目用于非法用途***
# 使用`git clone https://github.com/WillowSauceR/tools`将本项目克隆到本地或直接下载本项目，然后使用python3来运行
## scan.py
### 用法: `python3 scan.py [IP]`
#### 描述: 扫描一个IP上的所有BE协议服务器，使用前建议安装[Npcap](https://npcap.com/dist/npcap-1.60.exe)，然后使用命令`pip install scapy`来安装依赖，基于scapy，基本不漏服

## send.py 
### 用法: `python3 send.py [IP] [端口] [载体包文件] [次数] [间隔:秒] [使用代理] [自动显示MOTD]`
#### 描述: 发包复现工具, 需要一个内含byte数据的文件，一般为.dmp后缀名
#### 注意：代理功能处于开发阶段，不建议使用。默认使用[GitHub上的代理](https://github.com/ShiftyTR/Proxy-List)，如果需要使用其他代理，请将socks5.txt文件填充为你的代理IP端口

## motd.py
### 用法: `python3 motd.py [IP] [端口]`
#### 描述: motd一个BE服务器，支持自动解析返回的数据

## scanall.py
### 用法: `python3 scanall.py`
#### 描述: 扫描全网端口为19132的服，需要配合[wireshark](https://mirrors.tuna.tsinghua.edu.cn/wireshark/win64/Wireshark-win64-3.6.2.exe)抓取返回包
##### wireshark参数:
##### 捕获过滤器: `not src host 你的局域网IP and udp and port 19132`
##### 显示过滤器: `udp.length > 75 && ip.src == 0.0.0.0/0`