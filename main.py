from tkinter import (ttk, Tk, PhotoImage, Canvas, filedialog, colorchooser, RIDGE, GROOVE, ROUND, Scale, HORIZONTAL)
import cv2
from tkinter import filedialog, messagebox
from PIL import Image
from PIL import ImageTk, Image
import tkinter as tk
import numpy as np


class FrontEnd:
  def __init__(self, master):
    self.master = master
    self.draw_ids = []
    self.menu_initialisation()
    self.x = 0  # Giá trị mặc định cho self.x
    self.y = 0  # Giá trị mặc định cho self.y

  def menu_initialisation(self):
    self.master.geometry('750x630+250+10')
    self.master.title('Photoshop')
    self.frame_header = ttk.Frame(self.master)
    self.frame_header.pack()

    ttk.Label(self.frame_header, text='\nChỉnh sửa ảnh\n').grid(row=0, column=2, columnspan=1)

    self.frame_menu = ttk.Frame(self.master)
    self.frame_menu.pack()
    self.frame_menu.config(relief=RIDGE, padding=(50, 15))

    ttk.Button(self.frame_menu, text="Chọn ảnh", command=self.upload_action).grid(row=0, column=0, columnspan=2,
      padx=5, pady=5, sticky='sw')

    ttk.Button(self.frame_menu, text="Cắt ảnh", command=self.crop_action).grid(row=1, column=0, columnspan=2, padx=5,
      pady=5, sticky='sw')

    ttk.Button(self.frame_menu, text="Vẽ", command=self.draw_action).grid(row=2, column=0, columnspan=2,
      padx=5, pady=5, sticky='sw')

    ttk.Button(self.frame_menu, text="Bộ lọc", command=self.filter_action).grid(row=3, column=0, columnspan=2,
      padx=5, pady=5, sticky='sw')

    ttk.Button(self.frame_menu, text="Làm mờ", command=self.blur_action).grid(row=4, column=0, columnspan=2,
      padx=5, pady=5, sticky='sw')

    ttk.Button(self.frame_menu, text="Xoay ảnh", command=self.rotate_action).grid(row=5, column=0, columnspan=2, padx=5,
      pady=5, sticky='sw')

    ttk.Button(self.frame_menu, text="Lật ảnh", command=self.flip_action).grid(row=6, column=0, columnspan=2, padx=5,
      pady=5, sticky='sw')

    ttk.Button(self.frame_menu, text="Lưu ảnh", command=self.save_action).grid(row=7, column=0, columnspan=2, padx=5,
      pady=5, sticky='sw')

    ttk.Button(self.frame_menu, text="Hình ảnh gốc", command=self.reset_to_original).grid(row=8, column=0, columnspan=2,
                                                                                          padx=5, pady=5, sticky='sw')

    self.canvas = Canvas(self.frame_menu, bg="gray", width=300, height=400)
    self.canvas.grid(row=0, column=3, rowspan=10)

    self.side_frame = ttk.Frame(self.frame_menu)
    self.side_frame.grid(row=0, column=4, rowspan=10)
    self.side_frame.config(relief=GROOVE, padding=(50, 15))

    self.apply_and_cancel = ttk.Frame(self.master)
    self.apply_and_cancel.pack()
    self.apply = ttk.Button(self.apply_and_cancel, text="Lưu thay đổi", command=self.apply_action).grid(row=0, column=0,
      columnspan=1, padx=5, pady=5, sticky='sw')

    ttk.Button(self.apply_and_cancel, text="Hủy thay đổi", command=self.cancel_action).grid(row=0, column=1, columnspan=1,
      padx=5, pady=5, sticky='sw')

    self.show_original = tk.BooleanVar()  # Tạo một biến kiểu BooleanVar để theo dõi trạng thái của checkbutton
    self.show_original.set(False)  # Ban đầu không xem ảnh gốc

    check_button = ttk.Checkbutton(self.apply_and_cancel, text="Xem ảnh gốc", variable=self.show_original,
                                   command=self.revert_action)
    check_button.grid(row=0, column=2, columnspan=1, padx=5, pady=5, sticky='sw')


    ttk.Button(self.master, text="Thoát", command=self.master.destroy).pack(padx=10, pady=10)



  def upload_action(self):
    self.canvas.delete("all")
    self.filename = filedialog.askopenfilename()

    # Kiểm tra tệp có phải là tệp ảnh hay không
    try:
      img = Image.open(self.filename)
      img.close()
      # Nếu không có lỗi xảy ra khi mở tệp, đó là tệp hình ảnh
      # Thực hiện việc đọc và hiển thị hình ảnh tại đây
      self.original_image = cv2.imread(self.filename)
      self.edited_image = cv2.imread(self.filename)
      self.filtered_image = cv2.imread(self.filename)
      self.display_image(self.edited_image)
    except (IOError, OSError):
      # Nếu có lỗi xảy ra khi mở tệp, đó không phải là tệp hình ảnh
      messagebox.showerror("Lỗi", "Tệp không phải là hình ảnh")

  # Kết hợp với phần code hiển thị hình ảnh và các biến như trước

  def crop_action(self):
    if not hasattr(self, 'filename') or not self.filename:
      messagebox.showwarning("Lỗi", "Vui lòng chọn ảnh trước khi thực hiện chức năng")
      return
    self.rectangle_id = 0
    # self.ratio = 0
    self.crop_start_x = 0
    self.crop_start_y = 0
    self.crop_end_x = 0
    self.crop_end_y = 0
    self.canvas.bind("<ButtonPress>", self.start_crop)
    self.canvas.bind("<B1-Motion>", self.crop)
    self.canvas.bind("<ButtonRelease>", self.end_crop)

  def start_crop(self, event):
    self.crop_start_x = event.x
    self.crop_start_y = event.y

  def crop(self, event):
    if self.rectangle_id:
      self.canvas.delete(self.rectangle_id)

    self.crop_end_x = event.x
    self.crop_end_y = event.y

    self.rectangle_id = self.canvas.create_rectangle(self.crop_start_x, self.crop_start_y, self.crop_end_x,
                                                     self.crop_end_y, width=1)

  def end_crop(self, event):
    if self.crop_start_x <= self.crop_end_x and self.crop_start_y <= self.crop_end_y:
      start_x = int(self.crop_start_x * self.ratio)
      start_y = int(self.crop_start_y * self.ratio)
      end_x = int(self.crop_end_x * self.ratio)
      end_y = int(self.crop_end_y * self.ratio)
    elif self.crop_start_x > self.crop_end_x and self.crop_start_y <= self.crop_end_y:
      start_x = int(self.crop_end_x * self.ratio)
      start_y = int(self.crop_start_y * self.ratio)
      end_x = int(self.crop_start_x * self.ratio)
      end_y = int(self.crop_end_y * self.ratio)
    elif self.crop_start_x <= self.crop_end_x and self.crop_start_y > self.crop_end_y:
      start_x = int(self.crop_start_x * self.ratio)
      start_y = int(self.crop_end_y * self.ratio)
      end_x = int(self.crop_end_x * self.ratio)
      end_y = int(self.crop_start_y * self.ratio)
    else:
      start_x = int(self.crop_end_x * self.ratio)
      start_y = int(self.crop_end_y * self.ratio)
      end_x = int(self.crop_start_x * self.ratio)
      end_y = int(self.crop_start_y * self.ratio)

    x = slice(start_x, end_x, 1)
    y = slice(start_y, end_y, 1)

    self.filtered_image = self.edited_image[y, x]
    self.display_image(self.filtered_image)

  def draw_action(self):
    if not hasattr(self, 'filename') or not self.filename:
      messagebox.showwarning("Lỗi", "Vui lòng chọn ảnh trước khi thực hiện chức năng")
      return

    self.color_code = ((255, 0, 0), '#ff0000')
    self.refresh_side_frame()
    self.canvas.bind("<ButtonPress>", self.start_draw)
    self.canvas.bind("<B1-Motion>", self.draw)
    self.draw_color_button = ttk.Button(self.side_frame, text="Chọn màu", command=self.choose_color)
    self.draw_color_button.grid(row=0, column=2, padx=5, pady=5, sticky='sw')

  def choose_color(self):
    color_tuple = colorchooser.askcolor(title="Chọn màu")
    if color_tuple:
        self.color_code = color_tuple
        # Cập nhật self.x và self.y vào giá trị mặc định
        self.x = 0
        self.y = 0
        self.draw(event=None)  # Gọi lại hàm draw với màu mới đã chọn

  def start_draw(self, event):
    self.x = event.x
    self.y = event.y

  def draw(self, event):
    if event:
        if hasattr(event, 'x') and hasattr(event, 'y'):
            if self.x and self.y:
                self.canvas.create_line(self.x, self.y, event.x, event.y, width=2, fill=self.color_code[-1], capstyle=ROUND, smooth=True)
                r, g, b = self.color_code[0]
                cv2.line(self.filtered_image, (int(self.x * self.ratio), int(self.y * self.ratio)),
                         (int(event.x * self.ratio), int(event.y * self.ratio)), (b, g, r), thickness=int(self.ratio * 2), lineType=8)
            self.x = event.x
            self.y = event.y

  def refresh_side_frame(self):
    try:
      self.side_frame.grid_forget()
    except:
      pass

    self.canvas.unbind("<ButtonPress>")
    self.canvas.unbind("<B1-Motion>")
    self.canvas.unbind("<ButtonRelease>")
    self.display_image(self.edited_image)
    self.side_frame = ttk.Frame(self.frame_menu)
    self.side_frame.grid(row=0, column=4, rowspan=10)
    self.side_frame.config(relief=GROOVE, padding=(50, 15))

  def filter_action(self):
    if not hasattr(self, 'filename') or not self.filename:
      messagebox.showwarning("Lỗi", "Vui lòng chọn ảnh trước khi thực hiện chức năng")
      return
    self.refresh_side_frame()
    ttk.Button(self.side_frame, text="Negative", command=self.negative_action).grid(row=0, column=2, padx=5, pady=5,
      sticky='se')

    ttk.Button(self.side_frame, text="Black And white", command=self.bw_action).grid(row=1, column=2, padx=5, pady=5,
      sticky='se')

    ttk.Button(self.side_frame, text="Sharpening", command=self.Sharpening_action).grid(row=2, column=2, padx=5, pady=5,
      sticky='se')

    ttk.Button(self.side_frame, text="Excessive Sharpening", command=self.ExSharpening_action).grid(row=3, column=2, padx=5, pady=5,
      sticky='se')

    ttk.Button(self.side_frame, text="Edge Enhancement", command=self.EdEnhancement_action).grid(row=4, column=2, padx=5, pady=5,
      sticky='se')

  def blur_action(self):
    if not hasattr(self, 'filename') or not self.filename:
      messagebox.showwarning("Lỗi", "Vui lòng chọn ảnh trước khi thực hiện chức năng")
      return
    self.refresh_side_frame()

    ttk.Label(self.side_frame, text="Mức 1").grid(row=0, column=2, padx=5, sticky='sw')
    self.gaussian_slider = Scale(self.side_frame, from_=0, to=256, orient=HORIZONTAL, command=self.gaussian_action)
    self.gaussian_slider.grid(row=1, column=2, padx=5, sticky='sw')

    ttk.Label(self.side_frame, text="Mức 2").grid(row=2, column=2, padx=5, sticky='sw')
    self.average_slider = Scale(self.side_frame, from_=0, to=256, orient=HORIZONTAL, command=self.averaging_action)
    self.average_slider.grid(row=3, column=2, padx=5, sticky='sw')

    ttk.Label(self.side_frame, text="Mức 3").grid(row=4, column=2, padx=5, sticky='sw')
    self.median_slider = Scale(self.side_frame, from_=0, to=256, orient=HORIZONTAL, command=self.median_action)
    self.median_slider.grid(row=5, column=2, padx=5, sticky='sw')

  def rotate_action(self):
    if not hasattr(self, 'filename') or not self.filename:
      messagebox.showwarning("Lỗi", "Vui lòng chọn ảnh trước khi thực hiện chức năng")
      return
    self.refresh_side_frame()
    ttk.Button(self.side_frame, text="Xoay trái", command=self.rotate_left_action).grid(row=0, column=2, padx=5,
      pady=5, sticky='sw')

    ttk.Button(self.side_frame, text="Xoay phải", command=self.rotate_right_action).grid(row=1, column=2, padx=5,
      pady=5, sticky='sw')

  def flip_action(self):
    if not hasattr(self, 'filename') or not self.filename:
      messagebox.showwarning("Lỗi", "Vui lòng chọn ảnh trước khi thực hiện chức năng")
      return
    self.refresh_side_frame()
    ttk.Button(self.side_frame, text="Lật dọc", command=self.vertical_action).grid(row=0, column=2, padx=5,
      pady=5, sticky='se')

    ttk.Button(self.side_frame, text="Lật ngang", command=self.horizontal_action).grid(row=1, column=2, padx=5,
      pady=5, sticky='se')

  def save_action(self):
    if not hasattr(self, 'filename') or not self.filename:
      messagebox.showwarning("Lỗi", "Vui lòng chọn ảnh trước khi thực hiện chức năng")
      return
    original_file_type = self.filename.split('.')[-1]
    filename = filedialog.asksaveasfilename()
    filename = filename + "." + original_file_type

    save_as_image = self.edited_image
    cv2.imwrite(filename, save_as_image)
    self.filename = filename

  def reset_to_original(self):
    if hasattr(self, 'original_image') and self.original_image is not None:
      self.edited_image = self.original_image.copy()
      self.filtered_image = self.original_image.copy()
      self.display_image(self.original_image)

  def negative_action(self):
    self.filtered_image = cv2.bitwise_not(self.edited_image)
    self.display_image(self.filtered_image)

  def Sharpening_action(self):
    kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
    self.filtered_image = cv2.filter2D(self.edited_image, -1, kernel)
    self.display_image(self.filtered_image)

  def ExSharpening_action(self):
    kernel = np.array([[1,1,1], [1,-7,1], [1,1,1]])
    self.filtered_image = cv2.filter2D(self.edited_image, -1, kernel)
    self.display_image(self.filtered_image)

  def EdEnhancement_action(self):
    kernel = np.array([[-1,-1,-1,-1,-1],  [-1,2,2,2,-1], [-1,2,8,2,-1], [-1,2,2,2,-1], [-1,-1,-1,-1,-1]])/8.0
    self.filtered_image = cv2.filter2D(self.edited_image, -1, kernel)
    self.display_image(self.filtered_image)

  def bw_action(self):
    self.filtered_image = cv2.cvtColor(self.edited_image, cv2.COLOR_BGR2GRAY)
    self.filtered_image = cv2.cvtColor(self.filtered_image, cv2.COLOR_GRAY2BGR)
    self.display_image(self.filtered_image)

  def averaging_action(self, value):
    value = int(value)
    if value % 2 == 0:
      value += 1
    self.filtered_image = cv2.blur(self.edited_image, (value, value))
    self.display_image(self.filtered_image)

  def gaussian_action(self, value):
    value = int(value)
    if value % 2 == 0:
      value += 1
    self.filtered_image = cv2.GaussianBlur(self.edited_image, (value, value), 0)
    self.display_image(self.filtered_image)

  def median_action(self, value):
    value = int(value)
    if value % 2 == 0:
      value += 1
    self.filtered_image = cv2.medianBlur(self.edited_image, value)
    self.display_image(self.filtered_image)

  def saturation_action(self, event):
    self.filtered_image = cv2.convertScaleAbs(self.filtered_image, alpha=1, beta=self.saturation_slider.get())
    self.display_image(self.filtered_image)

  def rotate_left_action(self):
    self.filtered_image = cv2.rotate(self.filtered_image, cv2.ROTATE_90_COUNTERCLOCKWISE)
    self.display_image(self.filtered_image)

  def rotate_right_action(self):
    self.filtered_image = cv2.rotate(self.filtered_image, cv2.ROTATE_90_CLOCKWISE)
    self.display_image(self.filtered_image)

  def vertical_action(self):
    self.filtered_image = cv2.flip(self.filtered_image, 0)
    self.display_image(self.filtered_image)

  def horizontal_action(self):
    self.filtered_image = cv2.flip(self.filtered_image, 2)
    self.display_image(self.filtered_image)

  def apply_action(self):
    if not hasattr(self, 'filename') or not self.filename:
      messagebox.showwarning("Lỗi", "Vui lòng chọn ảnh trước khi thực hiện chức năng")
      return
    self.edited_image = self.filtered_image
    self.display_image(self.edited_image)

  def cancel_action(self):
    if not hasattr(self, 'filename') or not self.filename:
      messagebox.showwarning("Lỗi", "Vui lòng chọn ảnh trước khi thực hiện chức năng")
      return
    self.display_image(self.edited_image)

  def revert_action(self):
    if not hasattr(self, 'filename') or not self.filename:
      messagebox.showwarning("Lỗi", "Vui lòng chọn ảnh trước khi thực hiện chức năng")
      return

    if not self.show_original.get():  # If the checkbox is unchecked
      self.display_image(self.edited_image)  # Display the most recent edited image
    else:
      self.display_image(self.original_image)  # Display the original image

  def display_image(self, image=None):
    self.canvas.delete("all")
    if image is None:
        if self.show_original.get(True):  # Nếu đang xem ảnh gốc, hiển thị ảnh gốc
            image = self.original_image.copy()
        else:
            image = self.edited_image.copy()  # Nếu không, hiển thị ảnh đã chỉnh sửa
    else:
        image = image

    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    height, width, channels = image.shape
    ratio = height / width

    new_width = width
    new_height = height

    if height > 400 or width > 300:
      if ratio < 1:
        new_width = 300
        new_height = int(new_width * ratio)
      else:
        new_height = 400
        new_width = int(new_height * (width / height))

    self.ratio = height / new_height
    self.new_image = cv2.resize(image, (new_width, new_height))

    self.new_image = ImageTk.PhotoImage(Image.fromarray(self.new_image))

    self.canvas.config(width=new_width, height=new_height)
    self.canvas.create_image(new_width / 2, new_height / 2, image=self.new_image)

mainWindow = Tk()
FrontEnd(mainWindow)
mainWindow.mainloop()