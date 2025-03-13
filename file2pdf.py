import os
import re
import time
import glob
import tempfile
from tqdm import tqdm
from PIL import Image
from PyPDF2 import PdfMerger

def get_image_format():
    """交互式选择图片格式"""
    print("请选择要转换的图片格式：")
    print("1. JPG/JPEG")
    print("2. WEBP")
    print("3. PNG")
    print("4. 所有图片格式（JPG/JPEG/WEBP/PNG）")
    
    choice = input("请输入数字选择（1-4）：").strip()
    format_map = {
        '1': ['.jpg', '.jpeg'],
        '2': ['.webp'],
        '3': ['.png'],
        '4': ['.jpg', '.jpeg', '.webp', '.png']
    }
    
    while choice not in format_map:
        print("⚠️ 无效输入，请重新选择")
        choice = input("请输入数字选择（1-4）：").strip()
    
    return format_map[choice]

def convert_images_to_pdf(images, output_pdf_path):
    """将一批图像转换为 PDF"""
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

def process_folder(input_folder, output_pdf_path, formats, batch_size=50):
    image_files = sorted(
        [os.path.join(input_folder, f) for f in os.listdir(input_folder) 
         if f.lower().endswith(tuple(formats))],
        key=lambda x: natural_sort_key(os.path.basename(x)) 
    )

    if not image_files:
        print(f"⏭️ 无 {formats} 文件: {input_folder}")
        return

    total_files = len(image_files)
    print(f"📊 总计需处理: {total_files} 张图片")

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
        merger.close()
        for f in glob.glob(os.path.join(temp_dir, '*')):
            try:
                os.remove(f)
            except PermissionError:
                time.sleep(0.1)
                os.remove(f)
        os.rmdir(temp_dir)

def main():
    # 选择图片格式1
    selected_formats = get_image_format()
    
    current_dir = os.getcwd()
    output_dir = os.path.join(current_dir, "result")
    os.makedirs(output_dir, exist_ok=True)

    # 配置需要处理的文件夹（修改这里）
    TARGET_FOLDERS = [
        "folder1","folder2","folder3"
    ]
    
    for folder_name in TARGET_FOLDERS:
        input_folder = os.path.join(current_dir, folder_name)
        output_pdf = os.path.join(output_dir, f"{folder_name}.pdf")
        
        if os.path.isdir(input_folder):
            print(f"\n📂 正在处理: {folder_name}")
            process_folder(input_folder, output_pdf, selected_formats, batch_size=50)
        else:
            print(f"⚠️ 跳过不存在的文件夹: {folder_name}")

if __name__ == "__main__":
    main()
