import tkinter as tk
from tkinter import messagebox
import pyaudio  
import wave  
import os  
import speech_recognition as sr


samplerate = 44100 
channels = 2  
duration = 0  
recording = None  
is_recording = False  


p = pyaudio.PyAudio()


def start_recording():
    global recording, is_recording
    is_recording = True
    status_label.config(text="Идёт запись...")

   
    stream = p.open(format=pyaudio.paInt16,
                    channels=channels,
                    rate=samplerate,
                    input=True,
                    frames_per_buffer=1024)

    frames = []  

    def record():
        while is_recording:
            data = stream.read(1024)
            frames.append(data)


    import threading
    recording_thread = threading.Thread(target=record, daemon=True)
    recording_thread.start()

    return stream, frames


def stop_recording():
    global is_recording
    if not is_recording:
        return

    is_recording = False
    status_label.config(text="Запись остановлена.")


def save_recording():
    global recording, is_recording

    if recording is None:
        messagebox.showerror("Ошибка", "Нет записи!")
        return

    filename = "record.wav"
    wf = wave.open(filename, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(pyaudio.PyAudio().get_sample_size(pyaudio.paInt16))
    wf.setframerate(samplerate)
    wf.writeframes(b''.join(recording)) 
    wf.close()
    status_label.config(text=f"Файл сохранён: {filename}")


def play_audio():
    try:
        filename = "record.wav"
        if not os.path.exists(filename):
            messagebox.showerror("Ошибка", "Файл не найден!")
            return

        wf = wave.open(filename, 'rb')
        stream = p.open(format=pyaudio.paInt16,
                        channels=wf.getnchannels(),
                        rate=wf.getframerate(),
                        output=True)

        data = wf.readframes(1024)
        while data:
            stream.write(data)
            data = wf.readframes(1024)

        stream.stop_stream()
        stream.close()
        wf.close()
        status_label.config(text="Воспроизведение завершено.")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось воспроизвести файл.\n{e}")


def recognize_audio():
    try:
        r = sr.Recognizer()

        with sr.AudioFile("record.wav") as source:
            audio = r.record(source)  

        text = r.recognize_google(audio, language="ru-RU")
        messagebox.showinfo("Распознанный текст", text)

    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось распознать речь.\n{e}")


root = tk.Tk()
root.title("🎤 Диктофон на Tkinter")


status_label = tk.Label(root, text="Ожидание действия...", font=("Arial", 14))
status_label.pack(pady=10)


btn_record = tk.Button(root, text="🔴 Запись", command=start_recording, font=("Arial", 14), width=20, bg="#ff5757")
btn_record.pack(pady=5)

btn_stop = tk.Button(root, text="⏸ Стоп", command=stop_recording, font=("Arial", 14), width=20)
btn_stop.pack(pady=5)

btn_save = tk.Button(root, text="💾 Сохранить", command=save_recording, font=("Arial", 14), width=20)
btn_save.pack(pady=5)

btn_play = tk.Button(root, text="▶ Воспроизвести", command=play_audio, font=("Arial", 14), width=20)
btn_play.pack(pady=5)

btn_ai = tk.Button(root, text="🤖 Распознать речь", command=recognize_audio, font=("Arial", 14), width=25)
btn_ai.pack(pady=10)


root.mainloop()
