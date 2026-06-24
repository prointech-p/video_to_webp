import cv2
import numpy as np
from PIL import Image, ImageFilter


def super_optimized_chromakey_simple(input_path, output_path, 
                                   scale=50, target_fps=15, quality=50,
                                   sharpen=False, sharpen_amount=1.0,
                                   crop_top=0, crop_bottom=0, crop_left=0, crop_right=0):
    """
    Параметры:
    - sharpen: применять ли увеличение резкости (True/False)
    - sharpen_amount: сила увеличения резкости (0.5-2.0, рекомендуется 1.0)
    - crop_top, crop_bottom, crop_left, crop_right: количество пикселей для обрезки с каждой стороны
    """
    
    cap = cv2.VideoCapture(input_path)
    original_fps = cap.get(cv2.CAP_PROP_FPS)
    print(original_fps)
    skip_ratio = max(1, int(original_fps / target_fps))
    print(skip_ratio)
    
    frames = []
    frame_count = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if frame_count % skip_ratio == 0:
            # Уменьшение разрешения
            if scale < 100:
                height, width = frame.shape[:2]
                new_width = int(width * scale / 100)
                new_height = int(height * scale / 100)
                frame = cv2.resize(frame, (new_width, new_height), 
                                 interpolation=cv2.INTER_AREA)
            
            # ОБРЕЗКА (если нужна)
            if crop_top > 0 or crop_bottom > 0 or crop_left > 0 or crop_right > 0:
                height, width = frame.shape[:2]
                frame = frame[crop_top:height-crop_bottom, crop_left:width-crop_right]
            
            # УВЕЛИЧЕНИЕ РЕЗКОСТИ (если включено)
            if sharpen:
                # Метод Unsharp Mask - правильное увеличение резкости
                gaussian = cv2.GaussianBlur(frame, (0, 0), 2.0)
                frame = cv2.addWeighted(frame, 1.0 + sharpen_amount, gaussian, -sharpen_amount, 0)
            
            # ПРОСТОЙ НО ЭФФЕКТИВНЫЙ МЕТОД
            
            # 1. Создаем базовую маску
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            
            # Широкий диапазон зеленого
            lower_green = np.array([30, 40, 40])
            upper_green = np.array([90, 255, 255])
            # lower_green = np.array([0, 0, 0])
            # upper_green = np.array([0, 0, 0])
            mask = cv2.inRange(hsv, lower_green, upper_green)
            
            # 2. Создаем градиентную маску для плавных краев
            mask = cv2.GaussianBlur(mask.astype(np.float32), (3,3), 0.5)
            mask = np.clip(mask, 0, 255).astype(np.uint8)
            
            # 3. Инвертируем и применяем с коррекцией
            mask_inv = 255 - mask
            
            # 4. Простой деспилл - уменьшаем зеленый в полупрозрачных областях
            rgba = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
            
            # Применяем альфа канал
            rgba[:, :, 3] = mask_inv
            
            frames.append(Image.fromarray(rgba))
        
        frame_count += 1
    
    cap.release()
    
    # if frames:
    #     duration = int(1000 / target_fps)
    #     frames[0].save(output_path, format='WEBP',
    #                   save_all=True, append_images=frames[1:],
    #                   duration=duration, loop=0, quality=quality)
        
    #     print(f"Готово! Сохранено {len(frames)} кадров")

    if frames:
        duration = int(1000 / target_fps)
        frames[0].save(output_path, format='WEBP', save_all=True, 
                      append_images=frames[1:], duration=duration, 
                      loop=0, quality=quality)
        return True, len(frames)
    return False, 0



if __name__ == "__main__":
    super_optimized_chromakey_simple('source/Krissy_sweater_3x4.mp4', 'result/Krissy_sweater_3x4_70_10_85_ss.webp', 
                         scale=80, target_fps=10, quality=90,
                         sharpen=True, sharpen_amount=0.5,
                         crop_top=0)