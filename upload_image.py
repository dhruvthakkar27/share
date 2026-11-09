import requests
import glob

 
def send_image(image_path,date_str):
    BOT_TOKEN = '7506164173:AAHYPDRHjy0RyM8pIvgTRgnyHmgyTXH1oAI'  
    CHAT_ID =-1003578344584
    url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto'
    with open(image_path, 'rb') as photo:
        response = requests.post(
            url,
            data={'chat_id': CHAT_ID,
                  'caption':image_path.split("/")[-1]},
            files={'photo': photo}
        )
    print("Image sent!" if response.ok else f"Failed: {response.text}")


def send_all_images(date_str,types):
    BASE_IMAGE_PATH = f"/home/ssve/github-repo/rpi-cam-yolo11-main/{types}/" + str(date_str)
    all_images = glob.glob(f"{BASE_IMAGE_PATH}/*")
    all_images = sorted(all_images)
    all_images = [all_images[-1]]
    for image in all_images:
        send_image(image,date_str)

if __name__ == "__main__":
    send_all_images("2025-11-22", "captured_images")
#send_image(IMAGE_PATH)