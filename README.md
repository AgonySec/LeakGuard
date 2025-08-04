# **LeakGuard** - 一款综合性安全检测工具

​																											![](https://badgen.net/github/stars/AgonySec/LeakGuard)

[English][url-docen]

## 介绍


一款基于 Python3 实现的综合性安全检测工具，用于检测邮箱和密码是否在公开泄露数据中出现，同时支持 GitHub 和 Google 关键字搜索以及 Hunter.io 邮箱搜索。该工具提供命令行界面（CLI）和图形用户界面（GUI）两种使用方式。


## 功能特点

- 邮箱泄露检测
- 密码泄露检测
- GitHub 关键字检测（支持自定义黑名单）
- Google 关键字检测
- Hunter.io 邮箱检测
- 图形用户界面（GUI）

### 功能特点

* **批量检测**：能够同时检测多个邮箱或密码是否在数据泄露中出现，支持文件批量导入
* **多平台搜索**：支持在 GitHub、Google 和 Hunter.io 平台搜索相关信息
* **双界面操作**：提供命令行和图形用户界面两种操作方式
* **自定义配置**：支持设置黑名单用户和敏感词过滤
* **多种输出格式**：支持 JSON 和 Excel (XLSX) 格式输出结果
* **Python 实现**：使用 Python 编写，跨平台运行

## 使用方法
### 环境准备
前提：使用 **`python3`** 版本运行，并配置 [config.json](file://D:\WorkSpace\DevSecTools\LeakGuard\config\config.json) 文件：

如果要使用 GitHub 关键字搜索，需要配置 GitHub 的 token：

![image-20250102112303207](assets/image-20250102112303207.png)



### 1. 下载项目

```
git clone https://github.com/AgonySec/LeakGuard
```

### 2. 配置依赖

   确保已安装 Python3 环境。然后通过 pip 安装所需的依赖库：

```go
pip3 install -r requirements.txt
```

### 3. 运行工具
LeakGuard 提供两种使用方式：

#### 命令行界面（CLI）

使用命令行工具运行脚本，并传入需要检测的邮箱或密码列表文件：
```python
python main.py

usage: main.py [-h] [-e EMAIL] [-ef EMAIL_FILE] [-p PASSWORD] [-pf PASSFILE] [-o OUTPUT] [-c] [-bU BU] [-sW SW]
               [-google GOOGLE_SEARCH] [-ggf GOOGLE_FILE] [-github GITHUB_SEARCH] [-gtf GITHUB_FILE]
               [-hunter HUNTER_SEARCH] [-m {json,xlsx}]

LeakGuard 邮箱、密码泄露和关键字 综合检测工具 By Agony

options:
  -h, --help            show this help message and exit
  -e EMAIL, --email EMAIL
                        输入要测试的邮箱地址
  -ef EMAIL_FILE, --email_file EMAIL_FILE
                        输入包含多个邮箱地址的文件路径
  -p PASSWORD, --password PASSWORD
                        输入要测试的密码
  -pf PASSFILE, --passFile PASSFILE
                        输入包含多个密码的文件路径
  -o OUTPUT, --output OUTPUT
                        输出文件名，不包含后缀，默认为Google_email_timestamp.json
  -c                    信息收集模式
  -bU BU                设置黑名单用户文件
  -sW SW                设置敏感词文件
  -google GOOGLE_SEARCH, --google_search GOOGLE_SEARCH
                        指定要提取的邮箱后缀，例如 @qq.com, 从Google搜索中提取指定域名邮箱
  -ggf GOOGLE_FILE, --google_file GOOGLE_FILE
                        从txt文件中读取邮箱后缀,进行谷歌搜索
  -github GITHUB_SEARCH, --github_search GITHUB_SEARCH
                        指定关键字,进行GitHub搜索
  -gtf GITHUB_FILE, --github_file GITHUB_FILE
                        指定关键字文件,进行GitHub批量搜索
  -hunter HUNTER_SEARCH, --hunter_search HUNTER_SEARCH
                        输入网站域名，hunter.io搜索邮箱
  -m {json,xlsx}, --mode {json,xlsx}
                        指定输出格式，支持 json 或 xlsx，默认为 xlsx

```
#### 图形用户界面（GUI）

运行图形界面版本：
![image-20250804112756279](assets/image-20250804112756279.png)

```python
 python gui.py
 
```
GUI 版本提供直观的操作界面，包含以下功能标签页：

1. **邮箱检测**：支持单个邮箱地址检测或批量邮箱文件检测
2. **密码检测**：支持单个密码检测或批量密码文件检测
3. **Google 搜索**：通过邮箱后缀搜索相关信息
4. **GitHub 搜索**：通过关键字在 GitHub 上搜索
5. **Hunter 搜索**：通过域名在 Hunter.io 上搜索邮箱
6. **设置**：配置输出文件名、格式以及黑名单和敏感词文件

## 检测说明

### 邮箱泄露检测

通过查询 [haveibeenbreached.com](https://haveibeenbreached.com/) API 检测邮箱是否在已知数据泄露事件中出现。

### 密码泄露检测

通过查询 [haveibeenpwned.com](https://haveibeenpwned.com/) API 检测密码是否在已知泄露的密码库中出现。**注意：这里的检测密码泄露逻辑，其实是在拿你输入的密码在公开泄露情报中比较，如果相同则视为密码泄露！跟检测的邮箱账号毫无关联！**

### GitHub 关键字搜索

在 GitHub 上搜索指定关键字，支持设置黑名单用户和敏感词过滤。

### Google 关键字搜索

通过指定邮箱后缀（如 @qq.com）在 Google 上搜索相关邮箱信息。

### Hunter.io 搜索

通过指定域名在 Hunter.io 上搜索相关邮箱信息。

## 注意事项

- 有必要解释清楚，**这里的检测密码泄露逻辑，其实是在拿你输入的密码在公开泄露情报中比较，如果相同则视为密码泄露！跟检测的邮箱账号毫无关联！**
- 作者纯菜鸡，代码有很多不合理的地方，目前也没更改，望各位大佬手下留情
- 起初只是一个邮箱泄露检测工具，后面功能越来越丰富，增加了 GitHub、谷歌关键字搜索，就变成现在这个模样，感觉有些臃肿。。。

## 贡献

欢迎对本项目进行贡献。如果您发现任何问题或有新功能的建议，请通过 GitHub Issues 提交。

## 许可证

本项目采用 [MIT License](LICENSE) 许可证。

---


　　欢迎使用！ 

[url-docen]: README_EN.md
