# Image2PDF-Pro
🚀 一个高效、易用的批量图片转PDF工具，支持 JPG/PNG/WEBP 等多种格式，专为 Windows 用户设计。
## 功能特点
- 支持批量处理，快速合并多张图片为单个PDF
- 自然文件名排序，确保顺序正确
- 友好的 GUI 界面，操作简单
- 支持自定义输出路径和文件格式
- 轻量级，无需额外依赖

## 使用场景
- 将扫描的图片转换为PDF文档
- 合并多张截图为一个PDF文件
- 快速生成电子书或报告

## file2pdf.py
可以在脚本中一次性设置所有的目标文件夹，然后等待输出即可。运行完成后，每个文件夹的内容都会合并成各自的pdf文件

**使用步骤：**

1. 将目标文件夹和file2pdf.py放在同一个文件夹里，即同级目录
2. 建立一个result文件夹
3. 更改代码中的TARGET_FOLDERS为用户的目标文件夹名称（见示例）
4. 在终端选择要转换的目标文件格式，输出的结果将存放在result文件夹下。

更改目标文件夹：
```python
def main():
    # 选择图片格式1
    ...
    # 配置需要处理的文件夹（修改这里）
    TARGET_FOLDERS = [
        "Folder1","Folder2","Folder3"
    ]
    ...
```
## file2pdf_GUIv3.0.py
提供一个带有界面的脚本，更加直观使用.

## file2pdf_GUIv3.0.exe
打包好的程序，直接使用，详见Release板块下载

## 目录结构
- archive：存放旧代码
- result：存放合并的pdf
- folder1、2、3：目标文件夹，文件顺序请自行排列，推荐数字排序
- file2pdf.py：转换脚本
- file2pdf_GUIv3.0.py：带GUI界面
- README.md
