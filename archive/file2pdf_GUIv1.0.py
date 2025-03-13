import os
import re
import time
import glob
import tempfile
import threading
from tqdm import tqdm
from PIL import Image
from PyPDF2 import PdfMerger
import PySimpleGUI as sg

# 设置新版主题
sg.theme("LightGrey1")  # 确认使用新版主题名称

# 自然排序算法
def natural_sort_key(s):
    return [int(text) if text.isdigit() else text.lower() 
            for text in re.split(r'(\d+)', s)]

# 核心转换函数
def process_folder(input_folder, output_pdf, formats, progress_callback, log_callback):
    try:
        image_files = sorted(
            [os.path.join(input_folder, f) for f in os.listdir(input_folder)
             if f.lower().endswith(tuple(formats))],
            key=lambda x: natural_sort_key(os.path.basename(x))
        )

        if not image_files:
            log_callback(f"⏭️ 无 {formats} 文件: {input_folder}")
            return False

        total_files = len(image_files)
        log_callback(f"📊 总计需处理: {total_files} 张图片")

        temp_dir = tempfile.mkdtemp()
        merger = PdfMerger()
        batch_count = 0
        batch_size = 50

        try:
            with tqdm(total=total_files, desc="处理进度") as pbar:
                for i in range(0, total_files, batch_size):
                    batch_files = image_files[i:i+batch_size]
                    images = []
                    
                    for file_path in batch_files:
                        try:
                            with Image.open(file_path) as img:
                                images.append(img.copy())
                            pbar.update(1)
                            progress = (i + len(images)) / total_files * 100
                            progress_callback(progress)
                        except Exception as e:
                            log_callback(f"⚠️ 加载失败: {os.path.basename(file_path)} - {str(e)}")
                            pbar.update(1)

                    temp_pdf = os.path.join(temp_dir, f"temp_{batch_count}.pdf")
                    if convert_images_to_pdf(images, temp_pdf, log_callback):
                        with open(temp_pdf, 'rb') as f:
                            merger.append(f)
                        batch_count += 1
                        log_callback(f"🔖 生成第 {batch_count} 个中间PDF（本批 {len(batch_files)} 张）")

                    for img in images:
                        img.close()

            with open(output_pdf, 'wb') as f:
                merger.write(f)
            log_callback("✅ 合并完成！")

        finally:
            merger.close()
            for f in glob.glob(os.path.join(temp_dir, '*')):
                try:
                    os.remove(f)
                except Exception as e:
                    log_callback(f"⚠️ 临时文件删除失败: {str(e)}")
            os.rmdir(temp_dir)

        return True

    except Exception as e:
        log_callback(f"❌ 发生严重错误: {str(e)}")
        return False

def convert_images_to_pdf(images, output_pdf_path, log_callback):
    try:
        if not images:
            return False

        images[0].convert('RGB').save(
            output_pdf_path,
            save_all=True,
            append_images=[img.convert('RGB') for img in images[1:]],
            resolution=100.0
        )
        return True
    except Exception as e:
        log_callback(f"❌ PDF生成失败: {os.path.basename(output_pdf_path)} - {str(e)}")
        return False

# GUI布局
layout = [
    [sg.Text('输入文件夹', size=(10,1)), sg.Input(key='-INPUT-'), sg.FolderBrowse()],
    [sg.Text('输出位置', size=(10,1)), sg.Input(key='-OUTPUT-'), sg.FileSaveAs("保存PDF", file_types=(("PDF Files", "*.pdf"),))],
    [sg.Text('文件格式', size=(10,1)), 
     sg.Combo(['JPG/JPEG', 'PNG', 'WEBP', '所有格式'], 
              default_value='JPG/JPEG', 
              key='-FORMAT-')],
    [sg.ProgressBar(100, orientation='h', size=(50,20), key='-PROGRESS-')],
    [sg.Multiline(size=(70,15), autoscroll=True, key='-LOG-', disabled=True)],
    [sg.Button('开始转换', key='-START-'), sg.Exit()]
]

window = sg.Window('图片转PDF工具 v3.0', layout, finalize=True)

# 全局变量
is_running = False

# 日志回调函数
def gui_log(message):
    window['-LOG-'].print(message)
    window.refresh()

# 进度回调函数
def gui_progress(percent):
    window['-PROGRESS-'].update_bar(percent)
    window.refresh()

# 转换线程
def conversion_thread(input_folder, output_pdf, formats):
    global is_running
    try:
        success = process_folder(
            input_folder=input_folder,
            output_pdf=output_pdf,
            formats=formats,
            progress_callback=gui_progress,
            log_callback=gui_log
        )
        if success:
            sg.popup_notify('转换完成!', title='完成')
    finally:
        is_running = False
        window['-START-'].update(disabled=False)

# 主事件循环
while True:
    event, values = window.read(timeout=100)
    
    if event in (sg.WINDOW_CLOSED, 'Exit'):
        break
        
    if event == '-START-':
        if is_running:
            continue
            
        # 验证输入
        input_folder = values['-INPUT-']
        output_pdf = values['-OUTPUT-']
        
        if not input_folder or not os.path.isdir(input_folder):
            sg.popup_error('请选择有效的输入文件夹!')
            continue
            
        if not output_pdf.endswith('.pdf'):
            output_pdf += '.pdf'
            
        # 设置文件格式
        format_map = {
            'JPG/JPEG': ['.jpg', '.jpeg'],
            'PNG': ['.png'],
            'WEBP': ['.webp'],
            '所有格式': ['.jpg', '.jpeg', '.png', '.webp']
        }
        selected_format = values['-FORMAT-']
        
        # 重置界面
        is_running = True
        window['-START-'].update(disabled=True)
        window['-LOG-'].update('')
        window['-PROGRESS-'].update_bar(0)
        
        # 启动线程
        threading.Thread(
            target=conversion_thread,
            args=(input_folder, output_pdf, format_map[selected_format]),
            daemon=True
        ).start()

window.close()