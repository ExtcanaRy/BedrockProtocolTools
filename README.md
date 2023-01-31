# ***本工具包所有内容基于GPL3.0开源，请勿将本项目用于非法用途。由使用本工具包造成的任何问题，作者概不负责！***

## 直接在 [Releases](https://github.com/WillowSauceR/BedrockProtocolTools/releases/latest) 页面下载最新的版本，然后解压打开其中的exe文件进行使用

## 或者使用 `git clone https://github.com/WillowSauceR/BedrockProtocolTools`将本项目克隆到本地或直接下载本项目，然后使用python3来运行

## scan.py

### 使用方法: `python3 scan.py [目标地址] -i [可选：发包间隔] -p [可选：本地端口]`

#### 描述: 扫描IP上的所有BE协议服务器

#### 注意：目标地址可以填域名，IP或者IP段。如 mc.163.com，11.4.5.14，191.191.81-255.0-255

## send.py

### 使用方法: `python3 send.py [目标地址] [载体包文件] -p [可选：端口：默认19132] -l [可选：次数，默认1] -i [可选：间隔:秒，默认10] -d(自动显示MOTD) -pu(使用代理) -pc [代理的国家，如cn, ru, us]`

#### 描述: 发包复现工具, 需要一个内含byte数据的文件，一般为.dmp后缀名

#### 注意：代理功能处于开发阶段，不建议使用。默认使用[GitHub上的代理](https://github.com/ShiftyTR/Proxy-List)，如果需要使用其他代理，请将socks5.txt文件填充为你的代理IP端口

#### 注意：目标地址可以填IP或域名。如11.4.5.14，sex.homo.com

## motd.py

### 使用方法: `python3 motd.py [目标地址] [端口] -t [可选：超时时间]`

#### 描述: motd一个BE服务器，支持自动解析返回的数据
