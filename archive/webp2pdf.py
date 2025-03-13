import os
from PIL import Image

# 配置区域：在这里填写需要处理的文件夹名称
TARGET_FOLDERS = ["新建文件夹"]  # 替换为你的实际文件夹名

def convert_folder_to_pdf(input_folder, output_folder):
    # 收集所有 .webp 文件并按文件名排序
    webp_files = [f for f in os.listdir(input_folder) if f.lower().endswith('.webp')]
    webp_files.sort()

    # 转换所有图片为 PIL Image 对象（自动处理透明通道）
    images = []
    for file in webp_files:
        file_path = os.path.join(input_folder, file)
        try:
            img = Image.open(file_path)
            if img.mode in ('RGBA', 'LA'):
                img = img.convert('RGB')  # 转换为 RGB 模式避免 PDF 保存错误
            images.append(img)
        except Exception as e:
            print(f"⚠️ 处理失败: {file_path} - {str(e)}")

    # 生成 PDF 文件名（使用原文件夹名）
    folder_name = os.path.basename(input_folder)
    pdf_path = os.path.join(output_folder, f"{folder_name}.pdf")

    # 合并图片为 PDF（第一张图作为基准）
    if images:
        try:
            images[0].save(
                pdf_path,
                save_all=True,
                append_images=images[1:],
                resolution=100.0  # 控制输出质量（可选）
            )
            print(f"✅ 已生成: {pdf_path}")
        except Exception as e:
            print(f"❌ PDF 生成失败: {pdf_path} - {str(e)}")

def main():
    current_dir = os.getcwd()
    output_dir = os.path.join(current_dir, "result")
    os.makedirs(output_dir, exist_ok=True)

    # 只遍历指定的目标文件夹
    for folder_name in TARGET_FOLDERS:
        folder_path = os.path.join(current_dir, folder_name)
        if os.path.exists(folder_path):
            print(f"\n📂 正在处理文件夹: {folder_name}")
            convert_folder_to_pdf(folder_path, output_dir)
        else:
            print(f"⚠️ 警告：目标文件夹 '{folder_name}' 不存在，已跳过")

if __name__ == "__main__":
    main()