"""                                               PRIVATE USE AND DERIVATIVE LICENSE AGREEMENT 

        By using this software (the "Software"), you (the "User") agree to the following terms:  

1. Grant of License:  
    The Software is licensed to you for personal and non-commercial purposes, as well as for incorporation into your own projects, whether for private or public release.  

2. Permitted Use:  
    - You may use the Software as part of a larger project and publish your program, provided you include appropriate attribution to the original author (the "Licensor").  
    - You may modify the Software as needed for your project but must clearly indicate any changes made to the original work.  

3. Restrictions:  
     - You may not sell, lease, or sublicense the Software as a standalone product.  
     - If using the Software in a commercial project, prior written permission from the Licensor is required.(Credit,Cr)
     - You may not change or (copy a part of) the original form of the Software.  

4. Attribution Requirement:  
      Any published program or project that includes the Software, in whole or in part, must include the following notice:  
      *"This project includes software developed by [Jynoqtra], © 2025. Used with permission under the Private Use and Derivative License Agreement."*  

5. No Warranty:  
      The Software is provided "as is," without any express or implied warranties. The Licensor is not responsible for any damage or loss resulting from the use of the Software.  

6. Ownership:  
      All intellectual property rights, including but not limited to copyright and trademark rights, in the Software remain with the Licensor.  

7. Termination:  
     This license will terminate immediately if you breach any of the terms and conditions set forth in this agreement.  

8. Governing Law:  
      This agreement shall be governed by the laws of [the applicable jurisdiction, without regard to its conflict of law principles].  

9. Limitation of Liability:  
     In no event shall the Licensor be liable for any direct, indirect, incidental, special, consequential, or punitive damages, or any loss of profits, revenue, data, or use, incurred by you or any third party, whether in an action in contract, tort (including but not limited to negligence), or otherwise, even if the Licensor has been advised of the possibility of such damages.  

            Effective Date: [2025]  

            © 2025 [Jynoqtra]

"""



import inspect
import functools
import tkinter as tk
from tkinter import simpledialog, messagebox;
import time
import cv2
import base64
from http.server import SimpleHTTPRequestHandler, HTTPServer
import socket
import os
import sys
import logging
import requests
import pyperclip
import pyttsx3
import speech_recognition as sr
import random,psutil,smtplib,subprocess,shutil,json,math,mouse,uuid,pyautogui
import smtplib
import threading
from better_profanity import profanity
import socketserver
import http.server
import re
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from textblob import TextBlob
import requests, re
from JynAi import JynAi
import pyautogui
def wait(key="s",num=1):
    if key == "s"or"S":time.sleep(num)
    elif key == "m"or"M":time.sleep(num*60)
    elif key == "h"or"H":time.sleep(num*3600)
    else:print("An error occurred. Please use 's' for seconds, 'm' for minutes, or 'h' for hours.")
def JynPopMod():print("Click to see about JynPopMod https://github.com/Jynoqtra/JynPopMod that made by Jynoqtra")
def switch_case(_v, _c, d=None): return _c.get(_v, d)() if callable(_c.get(_v, d)) else _c.get(_v, d)
def pop(message, title="Information"):tk.Tk().withdraw();messagebox.showinfo(title, message)
def popinp(_p, _t="Input"): return simpledialog.askstring(_t, _p) or None
def ifnull(_v, _d): return _d if _v is None or _v == "" else _v
def popp(_a, _b): return _a + _b
def pop_with_image(_m, _img_path, _t="Information"): _img = tk.PhotoImage(file=_img_path); tk.Tk().withdraw(); messagebox.showinfo(_t, _m, _icon=_img)
def set_theme(root, theme="light"): [root.configure(bg="black") for widget in root.winfo_children()] if theme == "dark" else [root.configure(bg="white") for widget in root.winfo_children()]
def pop_switch(c, d=None, n="User"):option = popinp("Select an option:", title=n);result = switch_case(option, c, d);pop(f"Selected: {result}", title="Result")
def track_interaction(widget_name, event_type):print(f"Interaction with {widget_name}: {event_type}")
def main_win():return tk.Tk()
def set_window_size(_root, width=300, height=200):_root.geometry(f"{width}x{height}");track_interaction("window", "size set")
def set_window_title(_root, _title):_root.title(_title);track_interaction("window", "title set")
def set_window_icon(_root, _icon_path):_root.iconbitmap(_icon_path);track_interaction("window", "icon set")
def minimize_window(_root):_root.iconify();track_interaction("window", "minimized")
def maximize_window(_root):_root.state('zoomed');track_interaction("window", "maximized")
def destroy_window(_root):_root.destroy();track_interaction("window", "destroyed")
def center_window(_root, width=300, height=200):_root.geometry(f"{width}x{height}+{(_root.winfo_screenwidth()//2)-(width//2)}+{(_root.winfo_screenheight()//2)-(height//2)}");track_interaction("window", "centered")
def set_window_bg_color(_root, color):_root.configure(bg=color);track_interaction("window", f"background color set to {color}")
def set_window_always_on_top(_root):_root.attributes("-topmost", True);track_interaction("window", "always on top set")
def remove_window_always_on_top(_root):_root.attributes("-topmost", False);track_interaction("window", "always on top removed")
def set_window_opacity(_root, opacity):_root.attributes("-alpha", opacity);track_interaction("window", f"opacity set to {opacity}")
def hide_window(_root):_root.withdraw();track_interaction("window", "hidden")
def show_window(_root):_root.deiconify();track_interaction("window", "shown")
def set_window_fixed_size(_root):_root.resizable(False, False);track_interaction("window", "fixed size set")
def enable_window_resizing(_root):_root.resizable(True, True);track_interaction("window", "resizing enabled")
def set_window_bg_image(_root, image_path):img = tk.PhotoImage(file=image_path);label = tk.Label(_root, image=img);label.place(relwidth=1, relheight=1);label.image = img;track_interaction("window", f"background image set from {image_path}")
def change_window_icon(_root, icon_path):_root.iconbitmap(icon_path);track_interaction("window", f"icon changed to {icon_path}")
def create_label(_root, _text):label = tk.Label(_root, text=_text);label.pack();label.bind("<Button-1>", lambda event: track_interaction("label", "clicked"));track_interaction("label", "created");return label
def create_button(_root, _text, _command):button = tk.Button(_root, text=_text, command=lambda: [track_interaction("button", "clicked"), _command()]);button.pack();track_interaction("button", "created");return button
def create_entry(_root):entry = tk.Entry(_root);entry.pack();entry.bind("<FocusIn>", lambda event: track_interaction("entry", "focused"));entry.bind("<FocusOut>", lambda event: track_interaction("entry", "unfocused"));track_interaction("entry", "created");return entry
def create_text_widget(_root, _width=30, _height=10):text_widget = tk.Text(_root, width=_width, height=_height);text_widget.pack();text_widget.bind("<KeyRelease>", lambda event: track_interaction("text widget", f"key released: {event.keysym}"));track_interaction("text widget", "created");return text_widget
def create_checkbox(_root, _text, _command):checkbox = tk.Checkbutton(_root, text=_text, command=lambda: [track_interaction("checkbox", "clicked"), _command()]);checkbox.pack();track_interaction("checkbox", "created");return checkbox
def create_radio_buttons(_root, _options, _command):
    var = tk.StringVar()
    for option in _options:radio_button = tk.Radiobutton(_root, text=option, variable=var, value=option, command=lambda: [track_interaction("radio button", "selected"), _command()]);radio_button.pack();track_interaction("radio buttons", "created");return var
def create_dropdown(_root, _options, _command):var = tk.StringVar();dropdown = tk.OptionMenu(_root, var, * _options, command=lambda _: [track_interaction("dropdown", "selected"), _command()]);dropdown.pack();track_interaction("dropdown", "created");return var
def create_listbox(_root, _items, _command):
    listbox = tk.Listbox(_root)
    for item in _items:listbox.insert(tk.END, item)
    listbox.pack();listbox.bind("<ButtonRelease-1>", lambda event: track_interaction("listbox", "item selected"));track_interaction("listbox", "created");return listbox
def create_canvas(_root, _width=400, _height=300):canvas = tk.Canvas(_root, width=_width, height=_height);canvas.pack();track_interaction("canvas", "created");return canvas
def create_progress_bar(_root):progress_bar = tk.Progressbar(_root, length=200, mode='indeterminate');progress_bar.pack();track_interaction("progress bar", "created");return progress_bar
def create_scrollbar(_root, _widget):scrollbar = tk.Scrollbar(_root, orient=tk.VERTICAL, command=_widget.yview);_widget.config(yscrollcommand=scrollbar.set);scrollbar.pack(side=tk.RIGHT, fill=tk.Y);track_interaction("scrollbar", "created");return scrollbar
def create_frame(_root):frame = tk.Frame(_root);frame.pack();track_interaction("frame", "created");return frame
def create_menu_bar(_root):menu_bar = tk.Menu(_root);_root.config(menu=menu_bar);track_interaction("menu bar", "created");return menu_bar
def bind_key_press(_root, _key, _function): _root.bind(_key, _function)
def bind_mouse_click(_root, _function): _root.bind("<Button-1>", _function)
def bind_mouse_enter(_widget, _function): _widget.bind("<Enter>", _function)
def bind_mouse_leave(_widget, _function): _widget.bind("<Leave>", _function)
def bind_mouse_wheel(_root, _function): _root.bind("<MouseWheel>", _function)
def trigger_event(_widget, _event): _widget.event_generate(_event)
def update_label_text(_label, _new_text): _label.config(text=_new_text)
def update_entry_text(_entry, _new_text): _entry.delete(0, tk.END); _entry.insert(0, _new_text)
def update_text_widget(_text_widget, _new_content): _text_widget.delete(1.0, tk.END); _text_widget.insert(tk.END, _new_content)
def update_checkbox_state(_checkbox, _state): _checkbox.select() if _state else _checkbox.deselect()
def update_radio_selection(_var, _value): _var.set(_value)
def update_progress_bar(_progress, _value): _progress["value"] = _value
def disable_widget(_widget): _widget.config(state=tk.DISABLED)
def enable_widget(_widget): _widget.config(state=tk.NORMAL)
def change_widget_bg_color(_widget, _color): _widget.config(bg=_color)
def change_widget_fg_color(_widget, _color): _widget.config(fg=_color)
def change_widget_font(_widget, _font_name, _font_size): _widget.config(font=(_font_name, _font_size))
def add_widget_border(_widget, _border_width=2, _border_color="black"): _widget.config(borderwidth=_border_width, relief="solid", highlightbackground=_border_color)
def pack_with_padding(_widget, _padx=10, _pady=10): _widget.pack(padx=_padx, pady=_pady)
def grid_widget(_widget, _row, _col, _rowspan=1, _columnspan=1): _widget.grid(row=_row, column=_col, rowspan=_rowspan, columnspan=_columnspan)
def place_widget(_widget, _x, _y): _widget.place(x=_x, y=_y)
def set_grid_widget_sticky(_widget, _sticky="nsew"): _widget.grid(sticky=_sticky)
def show_info_messagebox(_message): messagebox.showinfo("Information", _message)
def show_error_messagebox(_message): messagebox.showerror("Error", _message)
def show_warning_messagebox(_message): messagebox.showwarning("Warning", _message)
def ask_yes_no_question(_question): return messagebox.askyesno("Question", _question)
def ask_for_input(_prompt): return simpledialog.askstring("Input", _prompt)
def show_messagebox_with_image(_message, _image_path): _img = tk.PhotoImage(file=_image_path); messagebox.showinfo("Information", _message, icon=_img)
def show_confirmation_messagebox(_message): return messagebox.askokcancel("Confirmation", _message)
def create_modal_dialog(_root, _message): dialog = tk.Toplevel(_root); dialog.title("Modal Dialog"); tk.Label(dialog, text=_message).pack(); tk.Button(dialog, text="OK", command=dialog.destroy).pack()
def prn(pnt):return print(pnt)
def delayed_pop(message, delay=3):time.sleep(delay);pop(message)
def create_checkbox_widget(root, text, default=False):
    checkbox = create_checkbox(root, text, command=lambda: pop(f"Selected: {checkbox.isChecked()}"))
    if default:checkbox.setChecked(True)
def validate_input(prompt, valid_type, error_message="Invalid input!"):
    while True:
        user_input = popinp(prompt)
        if valid_type == "int" and user_input.isdigit():return int(user_input)
        elif valid_type == "float" and is_valid_float(user_input):return float(user_input)
        else:pop(error_message)
def is_valid_float(value):
    try:float(value);return True
    except ValueError:return False
def depop(message, delay=3):time.sleep(delay);pop(message)
def pfk(task_name, progress, total):progress_percentage = (progress / total) * 100;message = f"{task_name} - Progress: {progress_percentage:.2f}%";pop(message)
def so(options, prompt="Select an option:"):selection = pop_switch(options, default="Invalid selection", name=prompt);return selection
def msgbox(message): pop(message)
def aynq(question):response = pop_switch({"Yes": True, "No": False}, default=False, name=question) ;return response
def show_warning_messagebox(message): show_warning_messagebox(message)
def bind_key_press(root, key, function): bind_key_press(root, key, function)
def bind_mouse_click(root, function):bind_mouse_click(root, function)
def bind_mouse_enter(widget, function):bind_mouse_enter(widget, function)
def bind_mouse_leave(widget, function):bind_mouse_leave(widget, function)
def bind_mouse_wheel(root, function):bind_mouse_wheel(root, function)
def set_window_size(_root, width=300, height=200):
    _root.geometry(f"{width}x{height}")
    track_interaction("window", "size set")
def animate_widget(widget, start_x, start_y, end_x, end_y, duration=1000):
    for t in range(duration):progress = t / duration;new_x = start_x + (end_x - start_x) * progress;new_y = start_y + (end_y - start_y) * progress;widget.place(x=new_x, y=new_y);time.sleep(0.01)
def capture_photo():
    try:
        cap = cv2.VideoCapture(0);ret, frame = cap.read()
        if ret:filename = "captured_photo.jpg";cv2.imwrite(filename, frame);print(f"Saved Captured Photo: {filename}")
        cap.release()
    except Exception as e:print(f"Error capturing photo: {e}")
def record_video(duration=10):
    cap = cv2.VideoCapture(0);frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH));frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT));fourcc = cv2.VideoWriter_fourcc(*'XVID');out = cv2.VideoWriter('recorded_video.avi', fourcc, 20.0, (frame_width, frame_height));start_time = time.time()
    while True:
        ret, frame = cap.read()
        if not ret:break;out.write(frame)
        if time.time() - start_time > duration:break;cv2.imshow('Recording Video Press q To Stop.', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):break
    cap.release();out.release();cv2.destroyAllWindows();print("Video Recorded.")
def get_camera_resolution():cap = cv2.VideoCapture(0);width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH));height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT));print(f"Kamera çözünürlüğü: {width}x{height}");cap.release()
def camera_zoom(factor=2.0):
    cap = cv2.VideoCapture(0);ret, frame = cap.read()
    if ret:
        height, width = frame.shape[:2];new_width = int(width * factor);new_height = int(height * factor);zoomed_frame = cv2.resize(frame, (new_width, new_height));cv2.imshow("Zoomed In", zoomed_frame)
        if cv2.waitKey(0) & 0xFF == ord('q'):pass
    cap.release();cv2.destroyAllWindows()
def reverse_string(string):reversed_str = string[::-1];print(f"Reversed String: {reversed_str}")
def encode_base64(data):encoded = base64.b64encode(data.encode('utf-8'));print(f"Base64: {encoded.decode('utf-8')}")
def decode_base64(encoded_data):decoded = base64.b64decode(encoded_data);print(f"UB16: {decoded.decode('utf-8')}")
def timer_function(func, seconds):time.sleep(seconds);func()
def start_http_server(ip="0.0.0.0", port=8000):server_address = (ip, port);httpd = HTTPServer(server_address, SimpleHTTPRequestHandler);print(f"Server started on {ip}:{port}");httpd.serve_forever()
def stop_http_server():print("Stopping server...");exit(0)
def get_server_status(url="http://localhost:8000"):
    try:
        response = requests.get(url)
        if response.status_code == 200:print("Server is up and running.")
        else:print(f"Server is down. Status Code: {response.status_code}")
    except requests.exceptions.RequestException as e:print(f"Error connecting to server: {e}")
def set_server_timeout(timeout=10):socket.setdefaulttimeout(timeout);print(f"Server connection timeout set to {timeout} seconds.")
def upload_file_to_server(file_path, url="http://localhost:8000/upload"):
    with open(file_path, 'rb') as file:
        response = requests.post(url, files={'file': file})
        if response.status_code == 200:print(f"File successfully uploaded: {file_path}")
        else:print(f"File upload failed. Status Code: {response.status_code}")
def download_file_from_server(file_url, save_path):
    response = requests.get(file_url)
    if response.status_code == 200:
        with open(save_path, 'wb') as file:file.write(response.content);print(f"File downloaded: {save_path}")
    else:print(f"File download failed. Status Code: {response.status_code}")
class CustomRequestHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":self.send_response(200);self.send_header('Content-type', 'text/html');self.end_headers();self.wfile.write(b"Welcome! Server is running.")
        elif self.path == "/status":self.send_response(200);self.send_header('Content-type', 'application/json');self.end_headers();self.wfile.write(b'{"status": "online"}')
        else:self.send_response(404);self.end_headers()
def start_custom_http_server(ip="0.0.0.0", port=8000):server_address = (ip, port);httpd = HTTPServer(server_address, CustomRequestHandler);print(f"Custom server started on {ip}:{port}");httpd.serve_forever()
def set_server_access_logs(log_file="server_access.log"):logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(message)s');print(f"Access logs are being saved to {log_file}")
def get_server_logs(log_file="server_access.log"):
    try:
        with open(log_file, 'r') as log:logs = log.readlines();print("".join(logs))
    except FileNotFoundError:print(f"{log_file} not found.")
def restart_http_server():print("Restarting server...");os.execv(sys.executable, ['python'] + sys.argv)
def iftrue(Var, function):
    if Var:function()
def iffalse(Var, function):
    if not Var:function()
def replace(string,replacement,replacment):return string.replace(replacement,replacment)
def until(function,whattodo):
    while True:
        whattodo
        if function():break
def repeat(function, times):
    for _ in range(times):function()
def oncondit(condition, function_true, function_false):
    if condition:function_true()
    else:function_false()
def repeat_forever(function):
    while True:function()
def safe_run(func, *args, **kwargs):
    try:func(*args, **kwargs)
    except Exception as e:print(f"Error occurred in function {func.__name__}: {e}");return None
def copy_to_clipboard(text):pyperclip.copy(text)
def paste_from_clipboard():return pyperclip.paste()
def text_to_speech(text):engine = pyttsx3.init();engine.say(text);engine.runAndWait()
def speech_to_text():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:print("Say something...");audio = recognizer.listen(source)
    try:return recognizer.recognize_google(audio)
    except sr.UnknownValueError:return "Could not understand audio"
    except sr.RequestError:return "Could not request results"
def start_timer(seconds, callback):time.sleep(seconds);callback()
def generate_random_string(length=15):return ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@/-*_', k=length))
def find_files_by_extension(directory, extension):return [f for f in os.listdir(directory) if f.endswith(extension)]
def get_ip_address():return socket.gethostbyname(socket.gethostname())
def send_email(subject, body, to_email, mailname, mailpass):server = smtplib.SMTP('smtp.gmail.com', 587);server.starttls();server.login(mailname, mailpass);message = f"Subject: {subject}\n\n{body}";server.sendmail(mailname, to_email, message);server.quit()
def convert_image_to_grayscale(image_path, output_path):image = cv2.imread(image_path);gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY);cv2.imwrite(output_path, gray_image)
def play_audio(text):engine = pyttsx3.init();engine.say(text);engine.runAndWait()
def record_audio():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:print("Say something:");audio = recognizer.listen(source)
    try:return recognizer.recognize_google(audio)
    except sr.UnknownValueError:return "Sorry, I couldn't understand that."
    except sr.RequestError: return "Could not request results; check your network connection."
def get_cpu_usage():return psutil.cpu_percent(interval=1)
def get_memory_usage():return psutil.virtual_memory().percent
def open_url(url):subprocess.run(['open', url], check=True)
def create_zip_file(source_dir, output_zip):shutil.make_archive(output_zip, 'zip', source_dir)
def extract_zip_file(zip_file, extract_dir):shutil.unpack_archive(zip_file, extract_dir)
def capture_screenshot(output_path):screen = pyautogui.screenshot();screen.save(output_path)
def move_file(source, destination):shutil.move(source, destination)
def copy_file(source, destination):shutil.copy(source, destination)
def show_file_properties(file_path):stats = os.stat(file_path);return f"Size: {stats.st_size} bytes, Last Modified: {time.ctime(stats.st_mtime)}"
def check_website_status(url):response = requests.get(url);return response.status_code == 200
def run_shell_command(command):result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True);return result.stdout.decode(), result.stderr.decode()
def get_weather(city,api_key):url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}";response = requests.get(url);return response.json()
def monitor_file_changes(file_path, callback):
    last_modified = os.path.getmtime(file_path)
    while True:
        current_modified = os.path.getmtime(file_path)
        if current_modified != last_modified:last_modified = current_modified;callback();time.sleep(1)
def reverse_string(string):return string[::-1]
def calculate_factorial(number):
    if number == 0:return 1;return number * calculate_factorial(number - 1)
def swap_values(a, b):return b, a
def find_maximum(numbers):return max(numbers)
def find_minimum(numbers):return min(numbers)
def get_random_choice(choices):return random.choice(choices)
def generate_unique_id():return str(uuid.uuid4())
def concatenate_lists(list1, list2):return list1 + list2
def write_to_file(filename, content):
    with open(filename, 'w') as file:file.write(content)
def read_from_file(filename):
    with open(filename, 'r', encoding='utf-8' or 'utf-16') as file:
        return str(file.read())
def parse_json(json_string):return json.loads(json_string)
def create_file_if_not_exists(filename):
    if not os.path.exists(filename):
        with open(filename, 'w') as file:file.write('')
def create_directory(directory):
    if not os.path.exists(directory):os.makedirs(directory)
def send_http_request(url, method='GET', data=None):
    if method == 'GET': response = requests.get(url)
    elif method == 'POST':response = requests.post(url, data=data);return response.text
def get_cpu_templinux():
    if sys.platform == 'linux':return float(subprocess.check_output(["cat", "/sys/class/thermal/thermal_zone0/temp"])) / 1000;return None
def calculate_square_root(number):return math.sqrt(number)
def track_mouse_position(callback):
    def on_move(x, y):callback(x, y)
    with mouse.Listener(on_move=on_move) as listener:listener.join()
def show_error_messagebox(message):messagebox.showerror("Error", message)
def start_background_task(backtask):
    threading.Thread(target=backtask).start()
def nocrash(func): 
    def wrapper(*args, **kwargs):return safe_run(func, *args, **kwargs);return wrapper
def contains_swears(text):
    return profanity.contains_profanity(text)
def filter_swears_in_text(text):return profanity.censor(text)
def Trsl2sl(str):return replace(str,"\\","/" )
def speech_to_text_with_filter():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source);print("Listening for speech...")
        try:audio = recognizer.listen(source);text = recognizer.recognize_google(audio);cleaned_text = filter_swears_in_text(text);print(f"Filtered text: {cleaned_text}");return cleaned_text
        except sr.UnknownValueError:print("Sorry, I couldn't understand what you said.");return ""
        except sr.RequestError as e:print(f"Error with the speech recognition service: {e}");return ""
def get_system_uptime():return time.time() - psutil.boot_time()
def download_image_from_url(image_url, save_path):
    response = requests.get(image_url)
    if response.status_code == 200:
        with open(save_path, 'wb') as file:file.write(response.content);print(f"Image downloaded to {save_path}")
    else:print(f"Failed to download image. Status Code: {response.status_code}")
def monitor_new_files(directory, callback):
    known_files = set(os.listdir(directory))
    while True:
        current_files = set(os.listdir(directory));new_files = current_files - known_files
        if new_files:callback(new_files);known_files = current_files;time.sleep(1)
def check_if_file_exists(file_path):return os.path.exists(file_path)
def check_internet_connection():
    response = os.system("ping -c 1 google.com")
    if response == 0:return True
    else:return False
def create_web_server(directory, port=8000):
    os.chdir(directory)
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", port), handler) as httpd:print(f"Serving {directory} at http://localhost:{port}");httpd.serve_forever()
def create_web_server(html,port=8000):
    html_content = html
    class CustomHandler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):self.send_response(200);self.send_header('Content-type', 'text/html');self.end_headers();self.wfile.write(html_content.encode('utf-8'))
    with socketserver.TCPServer(("", port), CustomHandler) as httpd:print(f"Serving custom HTML page at http://0.0.0.0:{port}");print("Anyone on the same network can access this.(if not work use this http://127.0.0.1:8000)");httpd.serve_forever()
def uppercase_list(lst):return [item.upper() for item in lst]
def remove_duplicates(lst):return list(set(lst))
def find_index(lst, element):
    try:return lst.index(element)
    except ValueError:return -1
def random_element(lst):
    if lst:return random.choice(lst);return None
def validate_email(email):pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$';return bool(re.match(pattern, email))      
def split_into_chunks(text, chunk_size):return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
def genpass(SMW):
    current_time = int(time.time());sec = current_time;strongie = generate_random_string(200);wekui = generate_random_string(20);medumi = generate_random_string(125)
    def WK():wpr1 = generate_random_string(10);wpr2 = generate_unique_id();wpr3 = generate_random_string(10);return f"{wpr1}{sec}{wekui}{wpr2}{sec+2}{wpr3}"
    def MD():mpr1 = generate_random_string(15);mpr2 = generate_unique_id();mpr3 = generate_random_string(15);return f"{mpr2}{sec+2}{mpr2}{mpr2}{medumi}{mpr3}{mpr1}{mpr2}{wekui}{sec+2}{mpr2}{mpr3}{sec+213215+sec}{mpr2}{sec+2}{mpr3}"
    def SR():spr1 = generate_random_string(20);spr2 = generate_unique_id();spr3 = generate_random_string(20);return f"{spr2}{sec+2}{spr2}{strongie}{spr2}{spr3}{spr1}{spr2}{sec+2}{wekui}{spr2}{spr3}{sec+213215+sec}{spr2}{sec+2}{spr3}"
    if SMW == "Weak":return WK()
    elif SMW == "Medium":return MD()
    elif SMW == "Strong":return SR()
    else:return None
def unique_elements(lst):return list(set(lst))
def sum_list(lst):return sum(lst)
def reverse_list(lst):return lst[::-1]
def is_prime(n):
    if n <= 1:return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:return False;return True
def shorten_text(text, length):return text[:length] + "..." if len(text) > length else text
def word_count(text):return len(text.split())
def is_valid_phone_number(phone_number):pattern = r'^\+?[1-9]\d{1,14}$';return re.match(pattern, phone_number) is not None
def clean_null(data):
    if isinstance(data, list):return [item for item in data if item not in [None, "", [], {}, False]]
    elif isinstance(data, dict):return {key: value for key, value in data.items() if value not in [None, "", [], {}, False]};return data
def calculate_average(numbers):
    if not numbers:return 0;return sum(numbers) / len(numbers)
def calculate_median(numbers):
    sorted_numbers = sorted(numbers);n = len(sorted_numbers);mid = n // 2
    if n % 2 == 0:return (sorted_numbers[mid - 1] + sorted_numbers[mid]) / 2;return sorted_numbers[mid]
def count_words(text):words = re.findall(r'\b\w+\b', text);return len(words)
def count_sentences(text):sentences = re.split(r'[.!?]', text);return len([s for s in sentences if s.strip()])
def word_frequencies(text):words = re.findall(r'\b\w+\b', text.lower());return dict(Counter(words))
def common_words(text1, text2):words1 = set(re.findall(r'\b\w+\b', text1.lower()));words2 = set(re.findall(r'\b\w+\b', text2.lower()));return list(words1 & words2)
def extract_keywords(text, n=5):vectorizer = TfidfVectorizer(stop_words='english', max_features=n);tfidf_matrix = vectorizer.fit_transform([text]);keywords = vectorizer.get_feature_names_out();return keywords
def evaluate_text_length(text):sentences = re.split(r'[.!?]', text);word_lengths = [len(word) for word in re.findall(r'\b\w+\b', text)];sentence_lengths = [len(sentence.split()) for sentence in sentences if sentence.strip()];avg_word_length = sum(word_lengths) / len(word_lengths) if word_lengths else 0;avg_sentence_length = sum(sentence_lengths) / len(sentence_lengths) if sentence_lengths else 0;return avg_word_length, avg_sentence_length
def sentiment_analysis(text):
    analysis = TextBlob(text)
    if analysis.sentiment.polarity > 0:return "Positive"
    elif analysis.sentiment.polarity < 0:return "Negative"
    else:return "Non Pos Non Neg"
def containsstr(string1, wic):
    def gefti(string, strip_chars=wic):matches = re.findall(f"[{re.escape(wic)}]", string);cleaned_matches = [match.strip(strip_chars) for match in matches if match];cleanret = ", ".join(cleaned_matches);return cleanret
    container1 = str(string1);container2 = gefti(container1, wic)
    if container2:return True
    else:return False
def split(string, strip_chars):cleaned_string = replace(string,strip_chars,"");return cleaned_string
def contamath_beta(string):
    symbols = [
        '+', '−', '±', '∓', '÷', '∗', '∙', '×', '∑', '⨊', '⅀', '∏', '∐', '∔', '∸', '≂', '⊕', '⊖', '⊗', '⊘', 
        '⊙', '⊚', '⊛', '⊝', '⊞', '⊟', '⊠', '⊡', '⋄', '⋇', '⋆', '⋋', '⋌', '~', '⩱', '⩲', '∀', '∞', '∃', '∄', '|', 
        '∤', '‱', '∇', '∘', '∻', '∽', '∾', '∿', '≀', '≁', '≬', '⊏', '⊐', '⊑', '⊒', '⋢', '⋣', '⊓', '⊔', '⊶', '⊷', 
        '⊸', '⊹', '⊺', '⋈', '⋉', '⋊', '⋮', '⋯', '⋰', '⋱', '⌈', '⌉', '⌊', '⌋', '〈', '〉', '⊲', '⊳', '⊴', '⊵', '⋪', 
        '⋫', '⋬', '⋭', '≠', '≈', '≂', '≃', '≄', '⋍', '≅', '≆', '≇', '≉', '≊', '≋', '≌', '≍', '≎', '≏', '≐', '≑', '≒', 
        '≓', '≔', '≕', '≖', '≗', '≙', '≚', '≜', '≟', '≡', '≢', '≭', '⋕', '^', '⁰', '¹', '²', '³', '⁴', '⁵', '⁶', '⁷', 
        '⁸', '⁹', '⁺', '⁻', '⁼', '⁽', '⁾', '√', '∛', '∜', '<', '>', '≤', '≥', '≦', '≧', '≨', '≩', '≪', '≫', '≮', '≯', 
        '≰', '≱', '≲', '≳', '≴', '≵', '≶', '≷', '≸', '≹', '≺', '≻', '≼', '≽', '≾', '≿', '⊀', '⊁', '⊰', '⋖', '⋗', 
        '⋘', '⋙', '⋚', '⋛', '⋞', '⋟', '⋠', '⋡', '⋦', '⋧', '⋨', '⋩', '∫', '∬', '∭', '∮', '∯', '∰', '∱', '∲', '∳', 
        '⨌', '⨍', '⨎', '⨏', '⨐', '⨑', '⨒', '⨓', '⨔', '⨕', '⨖', '⨗', '⨘', '⨙', '⨚', '⨛', '⨜', '⌀', '∠', 
        '∡', '∢', '⦛', '⦜', '⦝', '⦞', '⦟', '⦠', '⦡', '⦢', '⦣', '°', '⟂', '⏊', '⊥', '∥', '∦', '∝', '∟', '∺', 
        '≅', '⊾', '⋕', '⌒', '◠', '◡', '⊿', '△', '▷', '▽', '◁', '□', '▭', '▱', '○', '◊', '⋄', '→', '←', '↛', '↚', '↓', 
        '⇒', '⇐', '⇔', '⇋', '↯', '⇏', '∧', '∨', '⋀', '⋁', '⋂', '⋃', '¬', '≡', '∴', '∵', '∶', '∷', '∼', '⊧', '⊢', '⊣', 
        '⊤', '⊥', '⊨', '⊩', '⊪', '⊫', '⊬', '⊭', '⊮', '⊯', '⊻', '⊽', '⋎', '⋏', '∂', '𝛛', '𝜕', '𝝏', '𝞉', '𝟃', '∅', '∁', 
        '∈', '∉', '∋', '∌', '∖', '∩', '∪', '⊂', '⊃', '⊄', '⊅', '⊆', '⊇', '⊈', '⊉', '⊊', '⊋', '⊍', '⊎', '⋐', '⋑', 
        '⋒', '⋓', '⋔', '⋲', '⋳', '⋴', '⋵', '⋶', '⋷', '⋹', '⋺', '⋻', '⋼', '⋽', '⋾', '/', '*']
    for symbol in symbols:
        if symbol in string:return True
        else:return False
def Jai(q):return JynAi(q)
def add_commas(input_string):return ','.join(input_string)
def remove_spaces(text):return text.replace(" ", "")
def remove_spaces_andstickT(text):return re.sub(r'\s+', '', text)
def delfs(input_string, text_to_delete):return input_string.replace(text_to_delete, "")
def rem_alphabet(text):return ''.join([char for char in text if not char.isalpha()])
def hotdog(k1="",k2="",k3="",k4="",k5=""):pyautogui.hotkey(k1,k2,k3,k4,k5)
def keypress(key):pyautogui.keyDown(key);pyautogui.keyUp(key)
def isequal(s, eq):return s.lower() == eq.lower()
def contains(s, eq):return eq.lower() in s.lower()
class LoadingBar:
    def __init__(self, total_steps, bar_length=40):
        self.total_steps = total_steps
        self.bar_length = bar_length;self.progress = 0
    def load(self):
        self.progress += 1
        bar = '█' * (self.progress * self.bar_length // self.total_steps);spaces = ' ' * (self.bar_length - len(bar));sys.stdout.write(f'\rProcessing: |{bar}{spaces}| {((self.progress) / self.total_steps) * 100:.2f}%');sys.stdout.flush()
    def finish(self):sys.stdout.write(f'\rProcessing: |{"█" * self.bar_length}| 100.00%\n');sys.stdout.flush()
def track_function_start_end(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs): wrapper.bar.load();result = func(*args, **kwargs);return result
    return wrapper
def loading_bar(code):
    lines = code.splitlines();steps = sum(1 for line in lines if '(' in line and ')' in line);bar = LoadingBar(steps);track_function_start_end.bar = bar
    exec(code);bar.finish()
def its(i):sys.set_int_max_str_digits(99*99*99);return i
def parallel(*functions):
    threads = []
    for func in functions:
        thread = threading.Thread(target=func);threads.append(thread);thread.start()
    for thread in threads:thread.join()
def gs(func):return inspect.getsource(func)
def ccc(core_count, function, *args, **kwargs):
    total_cores = os.cpu_count()
    if core_count > total_cores:raise ValueError(f"Your input core count ({core_count}) cant be bigger than total core count ({total_cores}).");core_nums = list(range(core_count));p = psutil.Process(os.getpid());p.cpu_affinity(core_nums);return function(*args, **kwargs)
