import asyncio
from pathlib import Path
import cv2
import datetime

async def capture_and_save_image(filename):
    BASE_DIR = Path(__file__).parent.parent / "static" / "dir_cam_photo"
    filepath = BASE_DIR / filename

    cap = cv2.VideoCapture(1)  # 0 или 1 - в зависимости от количества камер
    await asyncio.sleep(2)
    ret, frame = cap.read()

    if ret:
        cv2.imwrite(str(filepath), frame)
        print(f"Изображение сохранено в {filepath}")
    else:
        print("Не удалось получить кадр с камеры")

    cap.release()
    return filename


async def main():
    filename = await capture_and_save_image(f'first_cam_{datetime.datetime.now()}.png')
    return filename

if __name__ == "__main__":
    print(asyncio.run(main()))
