# ***本工具包所有内容基于GPL3.0开源，请勿将本项目用于非法用途***

# 直接在releases页面下载最新的版本，然后解压打开其中的exe文件进行使用

# 或者使用 `git clone https://github.com/WillowSauceR/tools`将本项目克隆到本地或直接下载本项目，然后使用python3来运行

## scan.py

### 使用方法: `python3 scan.py [目标地址] [端口范围: 如1145-1919或all] [是否启用详细输出] [可选:超时时间，单位为秒，填0为不限] [可选:保存结果的文件名]`

#### 描述: 扫描IP上的所有BE协议服务器，使用前建议安装[Npcap](https://npcap.com/dist/npcap-1.60.exe)，然后使用命令 `pip install scapy`来安装依赖，基于scapy，基本不漏服

#### 注意：目标地址可以填域名，IP或者IP段。如 mc.163.com，11.4.5.14，191.191.81-255.0-255

## send.py

### 使用方法: `python3 send.py [目标地址] [端口] [载体包文件] [次数] [间隔:秒] [自动显示MOTD] [使用代理] [代理的国家，如cn, ru, us]`

#### 描述: 发包复现工具, 需要一个内含byte数据的文件，一般为.dmp后缀名

#### 注意：代理功能处于开发阶段，不建议使用。默认使用[GitHub上的代理](https://github.com/ShiftyTR/Proxy-List)，如果需要使用其他代理，请将socks5.txt文件填充为你的代理IP端口

## motd.py

### 使用方法: `python3 motd.py [目标地址] [端口]`

#### 描述: motd一个BE服务器，支持自动解析返回的数据
