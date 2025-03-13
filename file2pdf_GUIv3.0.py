import os
import re
import glob
import tempfile
import threading
from tqdm import tqdm
from PIL import Image
from PyPDF2 import PdfMerger
import PySimpleGUI as sg

sg.theme("LightGrey1")

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

# 修正后的GUI布局
layout = [
    [sg.Text('添加文件夹', size=(10,1)),
     sg.Input(key='-FOLDER-', enable_events=True, visible=False),
     sg.FolderBrowse('浏览', target='-FOLDER-'),
     sg.Button('清空列表', key='-CLEAR-')],
    [sg.Listbox([], size=(70,5), key='-FOLDER LIST-')],
    [sg.Text('输出目录', size=(10,1)), sg.Input(key='-OUTPUT-'), sg.FolderBrowse()],
    [sg.Text('文件格式', size=(10,1)), 
     sg.Combo(['JPG/JPEG', 'PNG', 'WEBP', '所有格式'], 
              default_value='JPG/JPEG', key='-FORMAT-')],
    [sg.ProgressBar(100, size=(50,20), key='-PROGRESS-')],
    [sg.Multiline(size=(70,15), key='-LOG-', autoscroll=True, disabled=True)],
    [sg.Button('开始转换', key='-START-'), sg.Exit()]
]

window = sg.Window('批量图片转PDF工具 v4.2', layout, finalize=True)

# 全局变量
current_folders = []
is_running = False

# 新增线程安全的事件队列
def gui_log(message):
    window.write_event_value('-LOG-', message)

def gui_progress(percent):
    window.write_event_value('-PROGRESS-', percent)

# 修改后的转换线程
def conversion_thread(input_folders, output_dir, formats):
    global is_running
    is_running = True
    try:
        total = len(input_folders)
        for idx, folder in enumerate(input_folders, 1):
            folder_name = os.path.basename(folder)
            output_pdf = os.path.join(output_dir, f"{folder_name}.pdf")
            gui_log(f"\n📂 正在处理文件夹 ({idx}/{total}): {folder_name}")
            
            # 调用核心处理
            success = process_folder(
                input_folder=folder,
                output_pdf=output_pdf,
                formats=formats,
                progress_callback=lambda x: gui_progress(x),
                log_callback=lambda m: gui_log(m)
            )
            
            if success:
                gui_log(f"✅ 成功生成：{os.path.basename(output_pdf)}")
            else:
                gui_log(f"❌ 转换失败：{folder_name}")
        
        window.write_event_value('-FINISH-', '所有转换完成!')
        
    except Exception as e:
        gui_log(f"❌ 发生全局错误：{str(e)}")
    finally:
        is_running = False
        window.write_event_value('-DONE-', '')

# 修正后的事件循环
while True:
    event, values = window.read()
    
    if event in (sg.WINDOW_CLOSED, 'Exit'):
        if is_running:
            sg.popup('请等待当前转换完成！')
            continue
        break
        
    if event == '-FOLDER-':
        new_path = values['-FOLDER-']
        if new_path:
            normalized_path = os.path.normpath(new_path)
            if normalized_path not in current_folders:
                current_folders.append(normalized_path)
                window['-FOLDER LIST-'].update(current_folders)
            window['-FOLDER-'].update('')
            
    if event == '-CLEAR-':
        current_folders = []
        window['-FOLDER LIST-'].update(current_folders)
        
    if event == '-START-':
        if is_running:
            continue
            
        input_folders = current_folders
        output_dir = values['-OUTPUT-']
        format_choice = values['-FORMAT-']
        
        if not input_folders:
            sg.popup_error('请至少选择一个输入文件夹!')
            continue
        if not output_dir:
            sg.popup_error('请选择输出目录!')
            continue
        
        try:
            os.makedirs(output_dir, exist_ok=True)
        except Exception as e:
            sg.popup_error(f'创建输出目录失败: {str(e)}')
            continue
        
        format_map = {
            'JPG/JPEG': ['.jpg', '.jpeg'],
            'PNG': ['.png'],
            'WEBP': ['.webp'],
            '所有格式': ['.jpg', '.jpeg', '.png', '.webp']
        }
        selected_formats = format_map[format_choice]
        
        window['-START-'].update(disabled=True)
        threading.Thread(
            target=conversion_thread,
            args=(input_folders, output_dir, selected_formats),
            daemon=True
        ).start()
    
    # 处理线程事件
    if event == '-LOG-':
        window['-LOG-'].print(values[event])
        window['-LOG-'].set_vscroll_position(1)
    
    if event == '-PROGRESS-':
        window['-PROGRESS-'].update_bar(values[event])
    
    if event == '-FINISH-':
        sg.popup_notify(values[event])
    
    if event == '-DONE-':
        window['-START-'].update(disabled=False)

window.close()