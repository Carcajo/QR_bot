import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer
from qrcode.image.styles.colormasks import HorizontalGradiantColorMask
from telebot import *
from telebot.types import *
from telebot.apihelper import ApiTelegramException
import cv2
import os

# Зависимости:
#     pip install qrcode
#     pip install pyTelegramBotAPI
#     pip install Pillow
#     pip install opencv-python

bot = TeleBot("6249459513:AAF1vkZiU50hVdIFS186tmRVMp5DbU6y7oc")


@bot.message_handler(commands=["start"])
def start(message: Message):
    bot.send_message(message.chat.id,
                     f"Здравствуйте, {message.from_user.first_name}!\n\nЭтот бот может генерировать и читать qr-коды.\nНажмите команду /create, чтобы создать qrcode.\nНажмите команду /decode чтобы прочитать qrcode.")


@bot.message_handler(commands=['create'])
def create(message: Message):
    bot.send_message(message.chat.id, 'Отправьте текст, который нужно вставить в qrcode:')
    bot.register_next_step_handler(message, get_text)


def get_text(message: Message):
    if message.text:
        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=30
        )


        qr.add_data(message.text)
        qr.make(fit=True)

        img = qr.make_image(image_factory=StyledPilImage,
                            color_mask=HorizontalGradiantColorMask(back_color=(255, 255, 255), left_color=(0, 100, 0),
                                                                   right_color=(255, 140, 0)), module_drawer=RoundedModuleDrawer(radius_ratio=1))
        try:
            bot.send_photo(message.chat.id, photo=img.get_image(),
                           caption=f"Автор - @Carcajo\n\nНажмите команду /create, чтобы создать qrcode.\nНажмите команду /decode чтобы прочитать qrcode.")
        except ApiTelegramException as e:
            if e.description == 'Bad Request: PHOTO_INVALID_DIMENSIONS':
                qr.box_size = 10

                qr.make(fit=True)

                img = qr.make_image(image_factory=StyledPilImage)
                try:
                    bot.send_photo(message.chat.id, photo=img.get_image(),
                                   caption=f"Автор - @Carcajo\n\nНажмите команду /create, чтобы создать qrcode.\nНажмите команду /decode чтобы прочитать qrcode.")
                except ApiTelegramException as e:
                    if e.description == 'Bad Request: PHOTO_INVALID_DIMENSIONS':
                        print(e)
                        bot.send_message(message.chat.id, f"Извините, но нам не удалось создать qrcode\n\nНажмите команду /create, чтобы создать qrcode.\nНажмите команду /decode чтобы прочитать qrcode.")
                    else:
                        raise e
            else:
                raise e
    else:
        bot.send_message(message.chat.id, 'Отправьте ТЕКСТ, который нужно вставить в qrcode:')
        bot.register_next_step_handler(message, get_text)

@bot.message_handler(commands=['decode'])
def decode(message: Message):
    bot.send_message(message.chat.id, "Отправьте картинку с qr кодом:")
    bot.register_next_step_handler(message, get_image)

def get_image(message: Message):
    if message.photo:
        photo = bot.download_file(bot.get_file(message.photo[-1].file_id).file_path)

        _, ext = os.path.splitext(bot.get_file(message.photo[-1].file_id).file_path)
        file_name = f"file_{message.photo[-1].file_id}{ext}"


        with open(file_name, "wb") as file:
            file.write(photo)

        img_qrcode = cv2.imread(file_name)

        os.remove(file_name)

        detector = cv2.QRCodeDetector()

        data, bbox, clear_qrcode = detector.detectAndDecode(img_qrcode)

        if data:
            bot.send_message(message.chat.id, "Содержание qr-кода:")
            bot.send_message(message.chat.id, data)
            bot.send_message(message.chat.id, "Автор - @Carcajo\n\nНажмите команду /create, чтобы создать qrcode.\nНажмите команду /decode чтобы прочитать qrcode.")
        else:
            bot.send_message(message.chat.id, f"Извините, но нам не удалось найти qrcode\n\nНажмите команду /create, чтобы создать qrcode.\nНажмите команду /decode чтобы прочитать qrcode.")
    else:
        bot.send_message(message.chat.id, "Отправьте КАРТИНКУ с qr кодом:")
        bot.register_next_step_handler(message, get_image)


bot.polling()