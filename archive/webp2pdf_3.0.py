#可以处理了，但是处理进度条不明显
import os
import glob
import tempfile
from PIL import Image
from PyPDF2 import PdfMerger

def convert_images_to_pdf(images, output_pdf_path):
    """将一批图像转换为 PDF"""
    if not images:
        return False

    try:
        # 转换为 RGB 模式并保存
        images[0].convert('RGB').save(
            output_pdf_path,
            save_all=True,
            append_images=[img.convert('RGB') for img in images[1:]],
            resolution=100.0
        )
        return True
    except Exception as e:
        print(f"❌ 生成中间 PDF 失败: {output_pdf_path} - {str(e)}")
        return False

def process_folder(input_folder, output_pdf_path, batch_size=50):
    """处理单个文件夹"""
    # 获取排序后的 WebP 文件列表
    webp_files = sorted(
        [os.path.join(input_folder, f) for f in os.listdir(input_folder) 
         if f.lower().endswith('.webp')],
        key=lambda x: os.path.getmtime(x)
    )

    if not webp_files:
        print(f"⏭️ 无 WebP 文件: {input_folder}")
        return

    # 创建临时目录存放中间 PDF
    with tempfile.TemporaryDirectory() as temp_dir:
        merger = PdfMerger()
        batch_count = 0

        # 分批次处理
        for i in range(0, len(webp_files), batch_size):
            batch_files = webp_files[i:i+batch_size]
            images = []
            
            # 加载当前批次图片
            for file_path in batch_files:
                try:
                    with Image.open(file_path) as img:
                        images.append(img.copy())
                except Exception as e:
                    print(f"⚠️ 加载失败: {os.path.basename(file_path)} - {str(e)}")

            # 生成中间 PDF
            temp_pdf = os.path.join(temp_dir, f"temp_{batch_count}.pdf")
            if convert_images_to_pdf(images, temp_pdf):
                merger.append(temp_pdf)
                batch_count += 1

            # 立即释放内存
            for img in images:
                img.close()

        # 合并所有中间 PDF
        if batch_count > 0:
            merger.write(output_pdf_path)
            print(f"✅ 成功生成: {output_pdf_path} (共 {len(webp_files)} 张图片)")
        else:
            print(f"❌ 未生成有效 PDF: {input_folder}")

        merger.close()

def main():
    current_dir = os.getcwd()
    output_dir = os.path.join(current_dir, "result")
    os.makedirs(output_dir, exist_ok=True)

    # 配置需要处理的文件夹（修改这里）
    TARGET_FOLDERS = ["协议换爱 _ 協議換愛  81-136","协议换爱 _ 協議換愛 137-161 END"]
    
    for folder_name in TARGET_FOLDERS:
        input_folder = os.path.join(current_dir, folder_name)
        output_pdf = os.path.join(output_dir, f"{folder_name}.pdf")
        
        if os.path.isdir(input_folder):
            print(f"\n📂 正在处理: {folder_name}")
            process_folder(input_folder, output_pdf, batch_size=50)
        else:
            print(f"⚠️ 跳过不存在的文件夹: {folder_name}")

if __name__ == "__main__":
    # 首次运行需要安装依赖
    # pip install pillow PyPDF2
    main()