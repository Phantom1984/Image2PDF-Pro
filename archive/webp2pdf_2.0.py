#废案，目的是相比1.0，可以合成大量的文件
import os
from PIL import Image

def convert_folder_to_pdf(input_folder, output_folder, batch_size=1):
    webp_files = sorted(
        [f for f in os.listdir(input_folder) if f.lower().endswith('.webp')],
        key=lambda x: os.path.getmtime(os.path.join(input_folder, x))  # 按修改时间排序
    )
    # 分块处理避免内存爆炸
    total_files = len(webp_files)
    folder_name = os.path.basename(input_folder)
    pdf_path = os.path.join(output_folder, f"{folder_name}.pdf")

    if total_files == 0:
        print(f"⏭️ 空文件夹: {input_folder}")
        return

    # 初始化基准图像
    first_image = None
    try:
        # 加载第一张图片作为基准
        first_path = os.path.join(input_folder, webp_files[0])
        with Image.open(first_path) as img:
            first_image = img.convert('RGB') if img.mode in ('RGBA', 'LA') else img.copy()
        
        # 分块处理剩余图片
        images = [first_image]
        for i in range(1, total_files):
            file_path = os.path.join(input_folder, webp_files[i])
            try:
                with Image.open(file_path) as img:
                    # 转换为 RGB 并缩小尺寸（可选）
                    processed_img = img.convert('RGB')
                    # processed_img = processed_img.resize((int(processed_img.width*0.5), int(processed_img.height*0.5)))  # 缩小50%
                    images.append(processed_img.copy())  # 复制后立即关闭原图

                # 每处理 batch_size 张图保存一次中间结果
                if i % batch_size == 0 or i == total_files-1:
                    first_image.save(
                        pdf_path,
                        save_all=True,
                        append_images=images[1:],
                        resolution=72.0,  # 降低分辨率到 72dpi
                        quality=85       # 适当降低质量
                    )
                    print(f"▌ 已处理 {i+1}/{total_files} 张")
                    # 清空已处理的图像列表（保留第一张作为基准）
                    for img in images[1:]:
                        img.close()
                    images = [first_image]

            except Exception as e:
                print(f"⚠️ 处理失败: {os.path.basename(file_path)} - {str(e)}")

        print(f"✅ 已完成: {pdf_path} (共 {total_files} 张)")

    finally:
        # 确保关闭所有图像对象
        if first_image:
            first_image.close()

def main():
    current_dir = os.getcwd()
    output_dir = os.path.join(current_dir, "result")
    os.makedirs(output_dir, exist_ok=True)

    # 只处理这些文件夹（根据实际情况修改）
    TARGET_FOLDERS = ["新建文件夹"]

    for folder_name in TARGET_FOLDERS:
        folder_path = os.path.join(current_dir, folder_name)
        if os.path.exists(folder_path):
            print(f"\n📂 开始处理: {folder_name}")
            convert_folder_to_pdf(folder_path, output_dir)
        else:
            print(f"⚠️ 文件夹不存在: {folder_name}")

if __name__ == "__main__":
    main()