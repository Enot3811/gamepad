import customtkinter
import os
from PIL import Image
import inputs_lib
import threading
from threading import Thread
import time
import serial
import tkinter
import numpy as np
import ctypes
import platform
import serial
import sys






class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.WIN = True if platform.system() == 'Windows' else False
        self.NIX = True if platform.system() == 'Linux' else False

        self.trig = 1
        self.previous_stick_timestamp = None  # Последняя временная метка со стика
        self.timestamp_delta = 1.5  # Требуемая разница между временными метками
        self.channel_list = ['', '', '', '', '', '', '', '']
        self.stick_sensity = np.array([[1., 1., 1., 1., 1., 1., 1., 1., 1.],
                                      [1., 1., 1., 1., 1., 1., 1., 1., 1.],
                                      [1., 1., 1., 1., 1., 1., 1., 1., 1.],
                                      [1., 1., 1., 1., 1., 1., 1., 1., 1.],
                                      [1., 1., 1., 1., 1., 1., 1., 1., 1.],
                                      [1., 1., 1., 1., 1., 1., 1., 1., 1.],
                                      [1., 1., 1., 1., 1., 1., 1., 1., 1.],
                                      [1., 1., 1., 1., 1., 1., 1., 1., 1.]])

        self.aprox_models = np.ones((8, 10), dtype='float')
        self.com_port = ''


        self.title("Joy_fly_control")
        self.geometry("700x500")

        # set grid layout 1x2
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # load images with light and dark mode image
        image_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "images")
        self.logo_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "CustomTkinter_logo_single.png")), size=(26, 26))
        self.image_icon_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "image_icon_light.png")), size=(20, 20))
        self.joystik_image = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "joystik_dark.png")),
                                                 dark_image=Image.open(os.path.join(image_path, "joystik_light.png")), size=(20, 20))
        self.chat_image = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "chat_dark.png")),
                                                 dark_image=Image.open(os.path.join(image_path, "chat_light.png")), size=(20, 20))
        self.add_user_image = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "add_user_dark.png")),
                                                     dark_image=Image.open(os.path.join(image_path, "add_user_light.png")), size=(20, 20))

        # create navigation frame
        self.navigation_frame = customtkinter.CTkFrame(self, corner_radius=0)
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")
        self.navigation_frame.grid_rowconfigure(4, weight=1)

        self.navigation_frame_label = customtkinter.CTkLabel(self.navigation_frame, text="  Ручной полет", image=self.logo_image,
                                                             compound="left", font=customtkinter.CTkFont(size=15, weight="bold"))
        self.navigation_frame_label.grid(row=0, column=0, padx=20, pady=20)

        self.joystik_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Полет",
                                                   fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                   image=self.joystik_image, anchor="w", command=self.joystik_button_event)
        self.joystik_button.grid(row=3, column=0, sticky="ew")

        self.chanel_selector_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Каналы",
                                                      fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                      image=self.chat_image, anchor="w", command=self.chanel_selector_button_event)
        self.chanel_selector_button.grid(row=1, column=0, sticky="ew")

        self.settings_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Настройки",
                                                      fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                      image=self.add_user_image, anchor="w", command=self.settings_button_event)
        self.settings_button.grid(row=2, column=0, sticky="ew")

        # create joystik frame
        self.joystik_frame = customtkinter.CTkFrame(
            self, corner_radius=0, fg_color="transparent")
        self.joystik_frame.grid_columnconfigure(0, weight=3)
        self.joystik_frame.grid_columnconfigure(1, weight=1)
        self.joystik_frame.grid_rowconfigure(0, weight=1)
        self.joystik_frame.grid_rowconfigure(1, weight=2)
        self.joystik_frame.grid_rowconfigure(2, weight=1)

        self.joystik_frame_button_1 = customtkinter.CTkButton(
            self.joystik_frame, text="Старт", command=self.button_start_event)
        self.joystik_frame_button_1.grid(
            row=0, column=0, padx=10, pady=10, sticky="ew")

        self.textbox = customtkinter.CTkTextbox(self.joystik_frame)
        self.textbox.grid(row=1, column=0, padx=(
            10, 10), pady=(10, 10), sticky="nsew")

        if self.com_port == '':
            self.textbox.insert(
                "0.0", "Произведите выбор порта для \nотправки команд.\n\n")
        else:
            self.textbox.insert(
                "0.0", 'Выбран ' + self.com_port + "\nНажмите старт для обнаружения \nджойстика и запуска потока управления.\n\n")

        self.joystik_frame_button_2 = customtkinter.CTkButton(
            self.joystik_frame, text="Стоп", command=self.button_stop_event)
        self.joystik_frame_button_2.grid(
            row=2, column=0, padx=10, pady=10, sticky="ew")
        
        
        
        if self.WIN:
            self.combobox_com = customtkinter.CTkComboBox(self.joystik_frame, values=self.scan_com_win(), command=self.combobox_com_event)
        if self.NIX:
            self.combobox_com = customtkinter.CTkComboBox(self.joystik_frame, values=self.scan_com_nix(), command=self.combobox_com_event)
	
        self.combobox_com.grid(
            row=0, column=1, padx=10, pady=10, sticky="ew")
        self.combobox_com.set("Выберите")

        # create second frame
        self.second_frame = customtkinter.CTkFrame(
            self, corner_radius=0, fg_color="transparent")
        self.second_frame.grid_columnconfigure(0, weight=1)
        self.second_frame.grid_columnconfigure(1, weight=1)
        self.second_frame.grid_columnconfigure(2, weight=1)

        self.second_frame.grid_rowconfigure(
            [0, 1, 2, 3, 4, 5, 6, 7, 8, 9], weight=1)

        self.second_frame_label_0 = customtkinter.CTkLabel(
            self.second_frame, text='Загрузка сохраненных \n параметров', width=120, height=25, fg_color="transparent", corner_radius=0)
        self.second_frame_label_0.grid(row=0, column=0, padx=10, pady=10)

        self.second_frame_label_1 = customtkinter.CTkLabel(
            self.second_frame, text='Переназначение \n (нажмите канал и клавишу)', width=120, height=25, fg_color="transparent", corner_radius=0)
        self.second_frame_label_1.grid(row=0, column=1, padx=10, pady=13)

        self.second_frame_label_2 = customtkinter.CTkLabel(
            self.second_frame, text='Сохранить текущую \n конфигурацию', width=120, height=25, fg_color="transparent", corner_radius=0)
        self.second_frame_label_2.grid(row=0, column=2, padx=10, pady=10)

        self.second_frame_btn_download = customtkinter.CTkButton(
            self.second_frame, text="Загрузить", command=self.btn_download_event)
        self.second_frame_btn_download.grid(
            row=1, column=0, padx=10, pady=10)

        self.second_frame_btn_ch_1 = customtkinter.CTkButton(
            self.second_frame, text="Канал 1", command=self.btn_ch_1_event)
        self.second_frame_btn_ch_1.grid(row=1, column=1, padx=10, pady=10)

        self.second_frame_btn_ch_2 = customtkinter.CTkButton(
            self.second_frame, text="Канал 2", command=self.btn_ch_2_event)
        self.second_frame_btn_ch_2.grid(row=2, column=1, padx=10, pady=10)

        self.second_frame_btn_ch_3 = customtkinter.CTkButton(
            self.second_frame, text="Канал 3", command=self.btn_ch_3_event)
        self.second_frame_btn_ch_3.grid(row=3, column=1, padx=10, pady=10)

        self.second_frame_btn_ch_4 = customtkinter.CTkButton(
            self.second_frame, text="Канал 4", command=self.btn_ch_4_event)
        self.second_frame_btn_ch_4.grid(row=4, column=1, padx=10, pady=10)

        self.second_frame_btn_ch_5 = customtkinter.CTkButton(
            self.second_frame, text="Канал 5", command=self.btn_ch_5_event)
        self.second_frame_btn_ch_5.grid(row=5, column=1, padx=10, pady=10)

        self.second_frame_btn_ch_6 = customtkinter.CTkButton(
            self.second_frame, text="Канал 6", command=self.btn_ch_6_event)
        self.second_frame_btn_ch_6.grid(row=6, column=1, padx=10, pady=10)

        self.second_frame_btn_ch_7 = customtkinter.CTkButton(
            self.second_frame, text="Канал 7", command=self.btn_ch_7_event)
        self.second_frame_btn_ch_7.grid(row=7, column=1, padx=10, pady=10)

        self.second_frame_btn_ch_8 = customtkinter.CTkButton(
            self.second_frame, text="Канал 8", command=self.btn_ch_8_event)
        self.second_frame_btn_ch_8.grid(row=8, column=1, padx=10, pady=10)

        self.second_frame_btn_save = customtkinter.CTkButton(
            self.second_frame, text="Сохранить", command=self.btn_save_event)
        self.second_frame_btn_save.grid(row=1, column=2, padx=10, pady=10)

        self.second_frame_btn_reset = customtkinter.CTkButton(
            self.second_frame, text="Сброс", command=self.btn_reset_event)
        self.second_frame_btn_reset.grid(row=3, column=2, padx=10, pady=10)

        # create third frame
        self.third_frame = customtkinter.CTkFrame(
            self, corner_radius=0, fg_color="transparent")
        self.third_frame.grid_columnconfigure(
            [0, 1, 2, 3, 4, 5, 6, 7, 8, 9], weight=1)
        self.third_frame.grid_rowconfigure(0, weight=1)
        self.third_frame.grid_rowconfigure(1, weight=1)

        self.channel_frame = customtkinter.CTkFrame(self.third_frame)
        self.channel_frame.grid(
            row=0, column=0, padx=10, pady=(10, 10), sticky="nsw")
        self.channel_frame.grid_columnconfigure(1, weight=1)
        self.channel_frame.grid_rowconfigure(
            [0, 1, 2, 3, 4, 5, 6, 7], weight=1)

        self.radiobutton_var = customtkinter.IntVar(value=0)

        self.radiobutton_1 = customtkinter.CTkRadioButton(
            self.channel_frame, text='Канал 1' + self.channel_list[0], command=self.radiobutton_event, variable=self.radiobutton_var, value=0)
        self.radiobutton_1.grid(
            row=0, column=0, padx=10, pady=10, sticky="w")

        self.radiobutton_2 = customtkinter.CTkRadioButton(
            self.channel_frame, text='Канал 2', command=self.radiobutton_event, variable=self.radiobutton_var, value=1)
        self.radiobutton_2.grid(
            row=1, column=0, padx=10, pady=10, sticky="w")

        self.radiobutton_3 = customtkinter.CTkRadioButton(
            self.channel_frame, text='Канал 3', command=self.radiobutton_event, variable=self.radiobutton_var, value=2)
        self.radiobutton_3.grid(
            row=2, column=0, padx=10, pady=10, sticky="w")

        self.radiobutton_4 = customtkinter.CTkRadioButton(
            self.channel_frame, text='Канал 4', command=self.radiobutton_event, variable=self.radiobutton_var, value=3)
        self.radiobutton_4.grid(
            row=3, column=0, padx=10, pady=10, sticky="w")

        self.radiobutton_5 = customtkinter.CTkRadioButton(
            self.channel_frame, text='Канал 5', command=self.radiobutton_event, variable=self.radiobutton_var, value=4)
        self.radiobutton_5.grid(
            row=4, column=0, padx=10, pady=10, sticky="w")

        self.radiobutton_6 = customtkinter.CTkRadioButton(
            self.channel_frame, text='Канал 6', command=self.radiobutton_event, variable=self.radiobutton_var, value=5)
        self.radiobutton_6.grid(
            row=5, column=0, padx=10, pady=10, sticky="w")

        self.radiobutton_7 = customtkinter.CTkRadioButton(
            self.channel_frame, text='Канал 7', command=self.radiobutton_event, variable=self.radiobutton_var, value=6)
        self.radiobutton_7.grid(
            row=6, column=0, padx=10, pady=10, sticky="w")

        self.radiobutton_8 = customtkinter.CTkRadioButton(
            self.channel_frame, text='Канал 8', command=self.radiobutton_event, variable=self.radiobutton_var, value=7)
        self.radiobutton_8.grid(
            row=7, column=0, padx=10, pady=10, sticky="w")

        self.slider_1 = customtkinter.CTkSlider(
            self.third_frame, command=self.slider_1_callback, from_=0, to=1, orientation="vertical")
        self.slider_1.grid(row=0, column=1, padx=10, pady=10, sticky='nsw')
        self.slider_1.set(self.stick_sensity[self.radiobutton_var.get(), 0])


        self.slider_2 = customtkinter.CTkSlider(
            self.third_frame, command=self.slider_2_callback, from_=0, to=1, orientation="vertical")
        self.slider_2.grid(row=0, column=2, padx=10, pady=10, sticky='nsw')
        self.slider_2.set(self.stick_sensity[self.radiobutton_var.get(), 1])

        self.slider_3 = customtkinter.CTkSlider(
            self.third_frame, command=self.slider_3_callback, from_=0, to=1, orientation="vertical")
        self.slider_3.grid(row=0, column=3, padx=10, pady=10, sticky='nsw')
        self.slider_3.set(self.stick_sensity[self.radiobutton_var.get(), 2])

        self.slider_4 = customtkinter.CTkSlider(
            self.third_frame, command=self.slider_4_callback, from_=0, to=1, orientation="vertical")
        self.slider_4.grid(row=0, column=4, padx=10, pady=10, sticky='nsw')
        self.slider_4.set(self.stick_sensity[self.radiobutton_var.get(), 3])

        self.slider_5 = customtkinter.CTkSlider(
            self.third_frame, command=self.slider_5_callback, from_=0, to=1, orientation="vertical")
        self.slider_5.grid(row=0, column=5, padx=10, pady=10, sticky='nsw')
        self.slider_5.set(self.stick_sensity[self.radiobutton_var.get(), 4])

        self.slider_6 = customtkinter.CTkSlider(
            self.third_frame, command=self.slider_6_callback, from_=0, to=1, orientation="vertical")
        self.slider_6.grid(row=0, column=6, padx=10, pady=10, sticky='nsw')
        self.slider_6.set(self.stick_sensity[self.radiobutton_var.get(), 5])

        self.slider_7 = customtkinter.CTkSlider(
            self.third_frame, command=self.slider_7_callback, from_=0, to=1, orientation="vertical")
        self.slider_7.grid(row=0, column=7, padx=10, pady=10, sticky='nsw')
        self.slider_7.set(self.stick_sensity[self.radiobutton_var.get(), 6])

        self.slider_8 = customtkinter.CTkSlider(
            self.third_frame, command=self.slider_8_callback, from_=0, to=1, orientation="vertical")
        self.slider_8.grid(row=0, column=8, padx=10, pady=10, sticky='nsw')
        self.slider_8.set(self.stick_sensity[self.radiobutton_var.get(), 7])

        self.slider_9 = customtkinter.CTkSlider(
            self.third_frame, command=self.slider_9_callback, from_=0, to=1, orientation="vertical")
        self.slider_9.grid(row=0, column=9, padx=10, pady=10, sticky='nsw')
        self.slider_9.set(self.stick_sensity[self.radiobutton_var.get(), 8])

        self.button_frame = customtkinter.CTkFrame(self.third_frame)
        self.button_frame.grid(
            row=1, column=0, padx=10, pady=(10, 10), sticky="ew", columnspan=10)
        self.button_frame.grid_columnconfigure(
            [self.radiobutton_var.get(), 1], weight=1)
        self.button_frame.grid_rowconfigure(
            [0, 1], weight=1)

        # Дописать функции вызова
        self.third_frame_btn_load = customtkinter.CTkButton(
            self.button_frame, text="Загрузить", command=self.btn_load_1_event)
        self.third_frame_btn_load.grid(
            row=0, column=0, padx=10, pady=(10, 10))
        # Дописать функции вызова
        self.third_frame_btn_reset = customtkinter.CTkButton(
            self.button_frame, text="Сброс", command=self.btn_reset_1_event)
        self.third_frame_btn_reset.grid(
            row=0, column=1, padx=10, pady=(10, 10))
        # Дописать функции вызова
        self.third_frame_btn_save = customtkinter.CTkButton(
            self.button_frame, text="Сохранить", command=self.btn_save_1_event)
        self.third_frame_btn_save.grid(
            row=0, column=2, padx=10, pady=(10, 10))

        # select default frame
        self.select_frame_by_name("chanel_selector")

    def btn_load_1_event(self):
        try:
            self.stick_sensity = np.load('sensity_settings.npy')
            self.third_frame_btn_label_1 = customtkinter.CTkLabel(
                self.button_frame, text='Файл загружен!', fg_color="transparent")
            self.third_frame_btn_label_1.grid(
                row=1, column=0, padx=10, pady=10)
            self.slider_1.set(
                self.stick_sensity[self.radiobutton_var.get(), 0])
            self.slider_2.set(
                self.stick_sensity[self.radiobutton_var.get(), 1])
            self.slider_3.set(
                self.stick_sensity[self.radiobutton_var.get(), 2])
            self.slider_4.set(
                self.stick_sensity[self.radiobutton_var.get(), 3])
            self.slider_5.set(
                self.stick_sensity[self.radiobutton_var.get(), 4])
            self.slider_6.set(
                self.stick_sensity[self.radiobutton_var.get(), 5])
            self.slider_7.set(
                self.stick_sensity[self.radiobutton_var.get(), 6])
            self.slider_8.set(
                self.stick_sensity[self.radiobutton_var.get(), 7])
            self.slider_9.set(
                self.stick_sensity[self.radiobutton_var.get(), 8])
            self.aprox_sensing()

        except:
            self.third_frame_btn_label_1 = customtkinter.CTkLabel(
                self.button_frame, text='Файл не найден!', fg_color="transparent")
            self.third_frame_btn_label_1.grid(
                row=1, column=0, padx=10, pady=10)


    def btn_reset_1_event(self):

        self.stick_sensity[self.radiobutton_var.get(), :] = 1.
        
        self.slider_1.set(self.stick_sensity[self.radiobutton_var.get(), 0])
        self.slider_2.set(self.stick_sensity[self.radiobutton_var.get(), 1])
        self.slider_3.set(self.stick_sensity[self.radiobutton_var.get(), 2])
        self.slider_4.set(self.stick_sensity[self.radiobutton_var.get(), 3])
        self.slider_5.set(self.stick_sensity[self.radiobutton_var.get(), 4])
        self.slider_6.set(self.stick_sensity[self.radiobutton_var.get(), 5])
        self.slider_7.set(self.stick_sensity[self.radiobutton_var.get(), 6])
        self.slider_8.set(self.stick_sensity[self.radiobutton_var.get(), 7])
        self.slider_9.set(self.stick_sensity[self.radiobutton_var.get(), 8])
        self.third_frame_btn_label_3 = customtkinter.CTkLabel(
            self.button_frame, text='Настройки текущего \n канала сброшены!', fg_color="transparent")
        self.third_frame_btn_label_3.grid(
            row=1, column=1, padx=10, pady=10)
        self.aprox_sensing()

        
        
    def btn_save_1_event(self):
        np.save('sensity_settings', self.stick_sensity)
        self.third_frame_btn_label_2 = customtkinter.CTkLabel(
            self.button_frame, text='Файл сохранен!', fg_color="transparent")
        self.third_frame_btn_label_2.grid(row=1, column=2)
        self.aprox_sensing()

    def radiobutton_event(self):
        self.slider_1.set(self.stick_sensity[self.radiobutton_var.get(), 0])
        self.slider_2.set(self.stick_sensity[self.radiobutton_var.get(), 1])
        self.slider_3.set(self.stick_sensity[self.radiobutton_var.get(), 2])
        self.slider_4.set(self.stick_sensity[self.radiobutton_var.get(), 3])
        self.slider_5.set(self.stick_sensity[self.radiobutton_var.get(), 4])
        self.slider_6.set(self.stick_sensity[self.radiobutton_var.get(), 5])
        self.slider_7.set(self.stick_sensity[self.radiobutton_var.get(), 6])
        self.slider_8.set(self.stick_sensity[self.radiobutton_var.get(), 7])
        self.slider_9.set(self.stick_sensity[self.radiobutton_var.get(), 8])
        self.aprox_sensing()
        print(self.radiobutton_var.get())


    def aprox_sensing(self):
        x = list(range(self.stick_sensity.shape[1]))
        x = np.array(x)
        x = x / np.max(x)
        for i in range(self.stick_sensity.shape[0]):
            y = self.stick_sensity[i, :]
            model = np.polyfit(x, y, 9)
            self.aprox_models[i, :] = model

    def set_sensing_settings(self, chanel, data):
        data = data / 255
        predict = np.poly1d(self.aprox_models[chanel, :])
        data = predict(data)
        print()
        if data > 1:
            data = 1
        if data < 0:
            data = 0
        return data
    

        

    def select_frame_by_name(self, name):
        # set button color for selected button
        self.joystik_button.configure(
            fg_color=("gray75", "gray25") if name == "joystik" else "transparent")
        self.chanel_selector_button.configure(fg_color=(
            "gray75", "gray25") if name == "chanel_selector" else "transparent")
        self.settings_button.configure(
            fg_color=("gray75", "gray25") if name == "settings" else "transparent")

        # show selected frame
        if name == "joystik":
            self.joystik_frame.grid(row=0, column=1, sticky="nsew")
            if self.WIN:
            	self.combobox_com.configure(values=self.scan_com_win())
            if self.NIX:
            	self.combobox_com.configure(values=self.scan_com_nix())
        else:
            self.joystik_frame.grid_forget()
        if name == "chanel_selector":
            self.second_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.second_frame.grid_forget()
        if name == "settings":
            self.radiobutton_1.configure(
                text='Канал 1 ' + self.channel_list[0])
            self.radiobutton_2.configure(
                text='Канал 2 ' + self.channel_list[1])
            self.radiobutton_3.configure(
                text='Канал 3 ' + self.channel_list[2])
            self.radiobutton_4.configure(
                text='Канал 4 ' + self.channel_list[3])
            self.radiobutton_5.configure(
                text='Канал 5 ' + self.channel_list[4])
            self.radiobutton_6.configure(
                text='Канал 6 ' + self.channel_list[5])
            self.radiobutton_7.configure(
                text='Канал 7 ' + self.channel_list[6])
            self.radiobutton_8.configure(
                text='Канал 8 ' + self.channel_list[7])
            
            self.third_frame.grid(row=0, column=1, sticky="nsew")

            self.aprox_sensing()
   
            
        else:
            self.third_frame.grid_forget()

    def joystik_button_event(self):
        self.select_frame_by_name("joystik")

    def chanel_selector_button_event(self):
        self.select_frame_by_name("chanel_selector")

    def settings_button_event(self):
        self.select_frame_by_name("settings")


    def button_start_event(self):
        self.aprox_sensing()

        # create textbox
        self.textbox = customtkinter.CTkTextbox(self.joystik_frame)
        self.textbox.grid(row=1, column=0, padx=(
            10, 10), pady=(20, 10), sticky="nsew")
        pads = inputs_lib.devices.gamepads
        if self.com_port == '':
            self.textbox.insert(
                "0.0", "Произведите выбор порта для \nотправки команд.\n\n")
        else:

            try:
                self.trig = 0
                self.thread.join()  # останавливаем предыдущий сеанс если он запущен
                time.sleep(1)
                self.trig = 1
                self.thread = Thread(target=self.threading_event)
                self.thread.start()
                thread_name = self.thread.name
                self.textbox.insert(
                    "0.0", "Команды отправляются в " + self.com_port + '\n\n')
                self.textbox.insert(
                    "0.0", f'Сеанс управления №:  {thread_name}' + '\n\n')
                self.textbox.insert(
                    "0.0", "Запущено ручное управление!\n\n" + "Джойстик: " + str(pads[0]) + '\n\n')
            except:
                self.trig = 1
                self.thread = Thread(target=self.threading_event)
                self.thread.start()
                thread_name = self.thread.name
                self.textbox.insert(
                    "0.0", "Команды отправляются в " + self.com_port + '\n\n')                
                self.textbox.insert(
                    "0.0", f'Сеанс управления №:  {thread_name}' + '\n\n')
                self.textbox.insert(
                    "0.0", "Запущено ручное управление!\n\n" + "Джойстик: " + str(pads[0]) + '\n\n')
  

    def button_stop_event(self):
        self.trig = 0
        self.textbox = customtkinter.CTkTextbox(self.joystik_frame)
        self.textbox.grid(row=1, column=0, padx=(
            10, 10), pady=(20, 10), sticky="nsew")
        try:
            self.thread.join()
            self.textbox.insert(
                "0.0", "Ручное управление остановлено!\n\n")
        except:
            self.textbox.insert(
                "0.0", "Не найдено сеансов управления!\n\n")
            
    def scan_com_win(self):
        list_com = []
        for i in range(256):
            try:
                name = 'COM' + str(i)
                s = serial.Serial(name)
                list_com.append(s.name)
                s.close()   # explicit close 'cause of delayed GC in java
            except serial.SerialException:
                pass
        return list_com
        
    def scan_com_nix(self):
        list_com = []
        for i in range(256):
            try:
                name = '/dev/ttyUSB'+str(i)
                s = serial.Serial(name)
                list_com.append(name)
                #s.close()
                name = '/dev/ttyACM'+str(i)
                s = serial.Serial(name)
                list_com.append(name)
                #s.close()
            except serial.SerialException:
                pass
        print(list_com)
        return list_com        
        

    def combobox_com_event(self, choice):
        self.com_port = self.combobox_com.get()
        if self.com_port == '':
            self.textbox.insert(
                "0.0", "Произведите выбор порта для \nотправки команд.\n\n")
        else:
            self.textbox.insert(
                "0.0", 'Выбран ' + self.com_port + "\nНажмите старт для обнаружения \nджойстика и запуска потока управления.\n\n")
        print(self.com_port)
         
       



    # Настройка каналов


    def clear_events(self):
        while True:
            try:
                events = inputs_lib.get_gamepad(blocking=False)
            except inputs_lib.UnpluggedError:
                time.sleep(1)
                break
            except inputs_lib.NoDataError:
                break

    def clear_events_nix(self):
        while True:
            #try:
                events = inputs_lib.get_gamepad(blocking=False)
                for event in events:
                    print(event.code)
            #except inputs_lib.UnpluggedError:
                #time.sleep(1)
                #break
            #except inputs_lib.NoDataError:
                #break                

    def get_valid_event(self):
        # Требуем событие до тех пор, пока не придёт нужное
        while True:
            event = inputs_lib.get_gamepad(blocking=True)[0]

            # Проверяем, что это кнопка, и что это нажатие (state == 1)
            got_valid_key_ev = event.ev_type == 'Key' and event.state == 1
            if got_valid_key_ev:
                break

            # Проверяем, что это стик со свежей временной меткой
            got_valid_stick_ev = (event.ev_type == 'Absolute' and (self.previous_stick_timestamp is None or
                                  event.timestamp - self.previous_stick_timestamp > self.timestamp_delta))
            if got_valid_stick_ev:
                self.previous_stick_timestamp = event.timestamp
                break
        return event
    
    def btn_ch_1_event(self):
        self.trig = 0
        if self.WIN:
            try:
                self.thread.join()
                self.clear_events()
                events = inputs_lib.get_gamepad(blocking=True)
                for event in events:
                    self.channel_list[0] = event.code
                    self.second_frame_btn_ch_1.configure(
		            text='Канал 1 ' + event.code)
                self.clear_events()
            except:
                self.clear_events()
                events = inputs_lib.get_gamepad(blocking=True)
                for event in events:
                    self.channel_list[0] = event.code
                    self.second_frame_btn_ch_1.configure(
		            text='Канал 1 ' + event.code)
                self.clear_events()  
                
        if self.NIX:
            try:
                self.thread.join()
                # self.clear_events_nix()
                events = inputs_lib.get_gamepad(blocking=True)
                for event in events:
                    self.channel_list[0] = event.code
                    self.second_frame_btn_ch_1.configure(
		            text='Канал 1 ' + event.code)
                # self.clear_events_nix()
            except:
                event = self.get_valid_event()
                self.channel_list[0] = event.code 
                self.second_frame_btn_ch_1.configure(text='Канал 1 ' + event.code)
            


    def btn_ch_2_event(self):
        self.trig = 0
        try:
            self.thread.join()
            # self.clear_events()
            events = inputs_lib.get_gamepad(blocking=True)
            for event in events:
                self.channel_list[1] = event.code
                self.second_frame_btn_ch_2.configure(
                    text='Канал 2 ' + event.code)
            # self.clear_events()
        except:
            event = self.get_valid_event()
            self.channel_list[1] = event.code 
            self.second_frame_btn_ch_2.configure(text='Канал 2 ' + event.code)

    def btn_ch_3_event(self):
        self.trig = 0
        try:
            self.thread.join() 
            # self.clear_events() 
            events = inputs_lib.get_gamepad(blocking=True)
            for event in events:
                self.channel_list[2] = event.code
                self.second_frame_btn_ch_3.configure(
                    text='Канал 3 ' + event.code)
            # self.clear_events()
        except:
            event = self.get_valid_event()
            self.channel_list[2] = event.code 
            self.second_frame_btn_ch_3.configure(text='Канал 3 ' + event.code)  

    def btn_ch_4_event(self):
        self.trig = 0
        try:
            self.thread.join()
            # self.clear_events()
            events = inputs_lib.get_gamepad(blocking=True)
            for event in events:
                self.channel_list[3] = event.code
                self.second_frame_btn_ch_4.configure(
                    text='Канал 4 ' + event.code)
            # self.clear_events()
        except:
            event = self.get_valid_event()
            self.channel_list[3] = event.code 
            self.second_frame_btn_ch_4.configure(text='Канал 4 ' + event.code)

    def btn_ch_5_event(self):
        self.trig = 0
        try:
            self.thread.join()
            # self.clear_events()  
            events = inputs_lib.get_gamepad(blocking=True)
            for event in events:
                self.channel_list[4] = event.code
                self.second_frame_btn_ch_5.configure(
                    text='Канал 5 ' + event.code)
            # self.clear_events()
        except:
            event = self.get_valid_event()
            self.channel_list[4] = event.code 
            self.second_frame_btn_ch_5.configure(text='Канал 5 ' + event.code)
        
    def btn_ch_6_event(self):
        self.trig = 0
        try:
            self.thread.join()
            # self.clear_events()
            events = inputs_lib.get_gamepad(blocking=True)
            for event in events:
                self.channel_list[5] = event.code
                self.second_frame_btn_ch_6.configure(
                    text='Канал 6 ' + event.code)
            # self.clear_events()
        except:
            event = self.get_valid_event()
            self.channel_list[5] = event.code
            self.second_frame_btn_ch_6.configure(
                text='Канал 6 ' + event.code)

    def btn_ch_7_event(self):
        self.trig = 0
        try:
            self.thread.join()
            # self.clear_events()
            events = inputs_lib.get_gamepad(blocking=True)
            for event in events:
                self.channel_list[6] = event.code
                self.second_frame_btn_ch_7.configure(
                    text='Канал 7 ' + event.code)
            # self.clear_events()
        except:
            event = self.get_valid_event()
            self.channel_list[6] = event.code
            self.second_frame_btn_ch_7.configure(
                text='Канал 7 ' + event.code)

    def btn_ch_8_event(self):
        self.trig = 0
        try:
            self.thread.join()
            # self.clear_events()
            events = inputs_lib.get_gamepad(blocking=True)
            for event in events:
                self.channel_list[7] = event.code
                self.second_frame_btn_ch_8.configure(
                    text='Канал 8 ' + event.code)
            # self.clear_events()
        except:
            event = self.get_valid_event()
            self.channel_list[7] = event.code
            self.second_frame_btn_ch_8.configure(
                text='Канал 8 ' + event.code)

    # Сохранение настроек в файл
    
    def btn_save_event(self):
        channel_settings = np.array(self.channel_list)
        np.save('channel_settings', channel_settings)
        self.second_frame_label_2 = customtkinter.CTkLabel(
            self.second_frame, text='Файл сохранен!', width=120, height=25, fg_color="transparent", corner_radius=0)
        self.second_frame_label_2.grid(row=2, column=2, padx=10, pady=10)
        

    # Сброс настроек
    
    def btn_reset_event(self):
        self.channel_list = ['', '', '', '', '', '', '', '']
        self.second_frame_btn_ch_1.configure(
            text='Канал 1 ' + str(self.channel_list[0]))
        self.second_frame_btn_ch_2.configure(
            text='Канал 2 ' + str(self.channel_list[1]))
        self.second_frame_btn_ch_3.configure(
            text='Канал 3 ' + str(self.channel_list[2]))
        self.second_frame_btn_ch_4.configure(
            text='Канал 4 ' + str(self.channel_list[3]))
        self.second_frame_btn_ch_5.configure(
            text='Канал 5 ' + str(self.channel_list[4]))
        self.second_frame_btn_ch_6.configure(
            text='Канал 6 ' + str(self.channel_list[5]))
        self.second_frame_btn_ch_7.configure(
            text='Канал 7 ' + str(self.channel_list[6]))
        self.second_frame_btn_ch_8.configure(
            text='Канал 8 ' + str(self.channel_list[7]))
        self.second_frame_label_2 = customtkinter.CTkLabel(
            self.second_frame, text='Настройки сброшены!', width=120, height=25, fg_color="transparent", corner_radius=0)
        self.second_frame_label_2.grid(row=4, column=2, padx=10, pady=10)


    def btn_download_event(self):
        try:
            channel_settings = np.load('channel_settings.npy')
            self.channel_list = list(channel_settings)
            self.second_frame_label_2 = customtkinter.CTkLabel(
                self.second_frame, text='Файл загружен!', width=120, height=25, fg_color="transparent", corner_radius=0)
            self.second_frame_label_2.grid(row=2, column=0, padx=10, pady=10)

            self.second_frame_btn_ch_1.configure(
                text='Канал 1 ' + str(self.channel_list[0]))
            self.second_frame_btn_ch_2.configure(
                text='Канал 2 ' + str(self.channel_list[1]))
            self.second_frame_btn_ch_3.configure(
                text='Канал 3 ' + str(self.channel_list[2]))
            self.second_frame_btn_ch_4.configure(
                text='Канал 4 ' + str(self.channel_list[3]))
            self.second_frame_btn_ch_5.configure(
                text='Канал 5 ' + str(self.channel_list[4]))
            self.second_frame_btn_ch_6.configure(
                text='Канал 6 ' + str(self.channel_list[5]))
            self.second_frame_btn_ch_7.configure(
                text='Канал 7 ' + str(self.channel_list[6]))
            self.second_frame_btn_ch_8.configure(
                text='Канал 8 ' + str(self.channel_list[7]))
            
        except:
            self.second_frame_label_2 = customtkinter.CTkLabel(
                self.second_frame, text='Файл не найден!', width=120, height=25, fg_color="transparent", corner_radius=0)
            self.second_frame_label_2.grid(row=2, column=0, padx=10, pady=10)

    def slider_1_callback(self, value):
        self.slider_1.set(value)
        self.stick_sensity[self.radiobutton_var.get(),
                                                    0] = self.slider_1.get()
        print(self.stick_sensity[self.radiobutton_var.get(), 0])
        print(self.radiobutton_var.get())
        self.aprox_sensing()
        
    def slider_2_callback(self, value):
        self.slider_2.set(value)
        self.stick_sensity[self.radiobutton_var.get(),
                                                    1] = self.slider_2.get()
        print(self.stick_sensity[self.radiobutton_var.get(), 1])
        self.aprox_sensing()
        
    def slider_3_callback(self, value):
        self.slider_3.set(value)
        self.stick_sensity[self.radiobutton_var.get(),
                                                    2] = self.slider_3.get()
        print(self.stick_sensity[self.radiobutton_var.get(), 2])
        self.aprox_sensing()

    def slider_4_callback(self, value):
        self.slider_4.set(value)
        self.stick_sensity[self.radiobutton_var.get(),
                                                    3] = self.slider_4.get()
        print(self.stick_sensity[self.radiobutton_var.get(), 3])
        self.aprox_sensing()
        
    def slider_5_callback(self, value):
        self.slider_5.set(value)
        self.stick_sensity[self.radiobutton_var.get(),
                                                    4] = self.slider_5.get()
        print(self.stick_sensity[self.radiobutton_var.get(), 4])
        self.aprox_sensing()
        
    def slider_6_callback(self, value):
        self.slider_6.set(value)
        self.stick_sensity[self.radiobutton_var.get(),
                                                    5] = self.slider_6.get()
        print(self.stick_sensity[self.radiobutton_var.get(), 5])
        self.aprox_sensing()

    def slider_7_callback(self, value):
        self.slider_7.set(value)
        self.stick_sensity[self.radiobutton_var.get(),
                                                    6] = self.slider_7.get()
        print(self.stick_sensity[self.radiobutton_var.get(), 6])
        self.aprox_sensing()

    def slider_8_callback(self, value):
        self.slider_8.set(value)
        self.stick_sensity[self.radiobutton_var.get(),
                                                    7] = self.slider_8.get()
        print(self.stick_sensity[self.radiobutton_var.get(), 7])
        self.aprox_sensing()
        
    def slider_9_callback(self, value):
        self.slider_9.set(value)
        self.stick_sensity[self.radiobutton_var.get(),
                                                    8] = self.slider_9.get()
        print(self.stick_sensity[self.radiobutton_var.get(), 8])
        self.aprox_sensing()



        
            


    # Чтение с джойстика и отправка в сериал порт

    def threading_event(self):

        serial_port = serial.Serial(
            port=self.com_port, baudrate=9600, timeout=0.1)
        serial_port.isOpen()
        while True:
            if self.trig == 0:
                serial_port.close()
                break            
            try:
                events = inputs_lib.get_gamepad(blocking=False)
                for event in events:
                    
                    if event.ev_type == 'Absolute' and (event.code in self.channel_list) == True:
                    
                        #print('event.ev_type', event.ev_type)
                        #print('event.code', event.code)
                        if self.WIN:
                            data = ctypes.c_ubyte(
                                ctypes.c_short(event.state).value).value
                        if self.NIX:
                            data = event.state
                        chanel = self.channel_list.index(event.code)
                        data = self.set_sensing_settings(chanel, data)
                        mess = ('$' + str(data) + ',' +
                                str(data) + ',' + str(data) + ';')
                        serial_port.write(mess.encode())
                        print('ch: ', chanel, ', value: ', data)
                    if event.ev_type == 'Key' and (event.code in self.channel_list) == True:
                        chanel = self.channel_list.index(event.code)
                        data = event.state
                        mess = ('$'+str(data)+','+str(data)+','+str(data)+';')
                        serial_port.write(mess.encode())
                        print('ch: ', chanel, ', value: ', data)                        

                    
            except inputs_lib.UnpluggedError:
                self.textbox.insert("0.0", "Джойстик не подключен!\n\n")
                time.sleep(1)
                continue
            except inputs_lib.NoDataError:
                continue

                     

            

if __name__ == "__main__":
    app = App()
    app.mainloop()
