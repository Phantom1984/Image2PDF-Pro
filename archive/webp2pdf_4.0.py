import os
import re
import time
import glob
import tempfile
from tqdm import tqdm  # 需要安装：pip install tqdm
from PIL import Image
from PyPDF2 import PdfMerger

def convert_images_to_pdf(images, output_pdf_path):
    if not images:
        return False
    try:
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

def natural_sort_key(s):
    """自然排序算法"""
    return [int(text) if text.isdigit() else text.lower()
            for text in re.split(r'(\d+)', s)]

def process_folder(input_folder, output_pdf_path, batch_size=50):
    image_files = sorted(
        [os.path.join(input_folder, f) for f in os.listdir(input_folder) 
         if f.lower().endswith('.webp')],
        key=lambda x: natural_sort_key(os.path.basename(x)) 
    )

    if not image_files:
        print(f"⏭️ 无 WebP 文件: {input_folder}")
        return

    total_files = len(image_files)
    print(f"📊 总计需处理: {total_files} 张图片")

    # 创建独立临时目录（避免跨文件夹冲突）
    temp_dir = tempfile.mkdtemp()
    try:
        merger = PdfMerger()
        batch_count = 0

        with tqdm(total=total_files, desc="🖼️ 加载图片", unit="img") as pbar:
            for i in range(0, total_files, batch_size):
                batch_files = image_files[i:i+batch_size]
                images = []
                
                for file_path in batch_files:
                    try:
                        with Image.open(file_path) as img:
                            images.append(img.copy())
                        pbar.update(1)
                    except Exception as e:
                        print(f"\n⚠️ 加载失败: {os.path.basename(file_path)} - {str(e)}")
                        pbar.update(1)

                temp_pdf = os.path.join(temp_dir, f"temp_{batch_count}.pdf")
                if convert_images_to_pdf(images, temp_pdf):
                    # 关键修复：显式关闭中间 PDF 文件句柄
                    with open(temp_pdf, 'rb') as f:
                        merger.append(f)
                    batch_count += 1
                    print(f"\n🔖 已生成第 {batch_count} 个中间 PDF（本批 {len(batch_files)} 张）")

                for img in images:
                    img.close()

        print(f"\n📂 开始合并 {batch_count} 个中间 PDF...")
        start_time = time.time()
        with open(output_pdf_path, 'wb') as f:
            merger.write(f)
        print(f"✅ 合并完成！耗时 {time.time()-start_time:.1f} 秒")

    finally:
        # 显式关闭 merger 并手动清理临时文件
        merger.close()
        # 安全删除临时目录
        for f in glob.glob(os.path.join(temp_dir, '*')):
            try:
                os.remove(f)
            except PermissionError:
                time.sleep(0.1)
                os.remove(f)
        os.rmdir(temp_dir)

def main():
    # ...（保持原 main 函数不变，可添加总文件夹进度）...
    current_dir = os.getcwd()
    output_dir = os.path.join(current_dir, "result")
    os.makedirs(output_dir, exist_ok=True)

    # 配置需要处理的文件夹（修改这里）
    TARGET_FOLDERS = ["协议换爱 _ 協議換愛  01-80","协议换爱 _ 協議換愛  81-136","协议换爱 _ 協議換愛 137-161 END"]
    
    for folder_name in TARGET_FOLDERS:
        input_folder = os.path.join(current_dir, folder_name)
        output_pdf = os.path.join(output_dir, f"{folder_name}.pdf")
        
        if os.path.isdir(input_folder):
            print(f"\n📂 正在处理: {folder_name}")
            process_folder(input_folder, output_pdf, batch_size=50)
        else:
            print(f"⚠️ 跳过不存在的文件夹: {folder_name}")

if __name__ == "__main__":
    main()