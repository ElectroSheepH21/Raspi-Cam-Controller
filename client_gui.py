import sys
import threading
from tkinter import ttk
import serial.tools.list_ports
import PIL
from PIL import Image, ImageTk
import cv2
from tkinter import *
import socket


class FancyGUI(Frame, object):
    # Frame ------------------------------------------------------------------------------------------------------------
    def __init__(self, master):
        super().__init__(master)

        self.lbl_video = None
        self.cbx_ports = None
        self.cbx_baud = None
        self.h_slide = None
        self.v_slide = None
        self.lbl_vid_connected = None
        self.lbl_tcp_connected = None
        self.lbl_serial_connected = None

        self.vid_port_var = StringVar()
        self.tcp_port_var = StringVar()
        self.cam_ip_var = StringVar()
        self.position_var = StringVar()
        self.position_var.set("[0:0]")
        self.position_old_var = StringVar()
        self.position_old_var.set(self.position_var.get())

        self.serial_obj = None
        self.baudrates = [9600, 115200]
        self.tcp_connected = False

        self.x = 0
        self.y = 0

        self.job_id_cross = None
        self.job_id_frame = None
        self.camera = None

        self.master.title("Camera controller")
        self.master.geometry("600x600")
        self.master.minsize(600, 600)
        self.master.protocol('WM_DELETE_WINDOW', self.on_close)
        self.createWidgets()
        self.update_serial_ports()

    def createWidgets(self):
        # Camera connection --------------------------------------------------------------------------------------------
        lblfrm_camera_connection = LabelFrame(self.master, text="Camera connection")
        lblfrm_camera_connection.pack(padx=4, pady=4, fill=X)

        frm_camera_config = Frame(lblfrm_camera_connection, bg="lightgray")
        frm_camera_config.pack(padx=4, pady=4, side=LEFT)

        # IP
        frm_ip = Frame(frm_camera_config, bg="lightgray")
        frm_ip.pack(padx=4, pady=4, anchor="w")
        Label(frm_ip, text="IP:", bg="lightgray").pack(padx=4, pady=4, side=LEFT)
        Entry(frm_ip, textvariable=self.cam_ip_var).pack(padx=4, pady=4, side=LEFT)
        self.cam_ip_var.set("192.168.1.134")

        # Video port
        frm_vid_port = Frame(frm_camera_config, bg="lightgray")
        frm_vid_port.pack(padx=4, pady=4, anchor="w")
        Label(frm_vid_port, text="Video port:", bg="lightgray").pack(padx=4, pady=4, side=LEFT)
        Entry(frm_vid_port, textvariable=self.vid_port_var).pack(padx=4, pady=4, side=LEFT)
        self.vid_port_var.set("8081")

        # TCP
        frm_tcp_port = Frame(frm_camera_config, bg="lightgray")
        frm_tcp_port.pack(padx=4, pady=4, anchor="w")
        Label(frm_tcp_port, text="TCP port:", bg="lightgray").pack(padx=4, pady=4, side=LEFT)
        Entry(frm_tcp_port, textvariable=self.tcp_port_var).pack(padx=4, pady=4, side=LEFT)
        self.tcp_port_var.set("9999")

        # Connect/disconnect buttons
        frm_connected = Frame(lblfrm_camera_connection, bg="lightgray")
        frm_connected.pack(padx=4, pady=4, side=LEFT, fill=Y)
        frm_buttons = Frame(frm_connected, bg="lightgray")
        frm_buttons.pack(padx=4, pady=4)
        Button(frm_buttons, text="Connect", command=self.connect).pack(padx=4, pady=4, side=LEFT)
        Button(frm_buttons, text="Disconnect", command=self.disconnect).pack(padx=4, pady=4, side=LEFT)
        frm_video_connected = Frame(frm_connected, bg="lightgray")
        frm_video_connected.pack(padx=4, pady=4)
        Label(frm_video_connected, text="Video:", bg="lightgray").pack(padx=4, pady=4, side=LEFT)
        self.lbl_vid_connected = Label(frm_video_connected, width=8, bg="red")
        self.lbl_vid_connected.pack(padx=4, pady=4, side=LEFT)
        frm_tcp_connected = Frame(frm_connected, bg="lightgray")
        frm_tcp_connected.pack(padx=4, pady=4)
        Label(frm_tcp_connected, text="TCP:", bg="lightgray").pack(padx=4, pady=4, side=LEFT)
        self.lbl_tcp_connected = Label(frm_tcp_connected, width=8, bg="red")
        self.lbl_tcp_connected.pack(padx=4, pady=4, side=LEFT)

        # Serial connection --------------------------------------------------------------------------------------------
        lblfrm_serial_connection = LabelFrame(self.master, text="Serial connection")
        lblfrm_serial_connection.pack(padx=4, pady=4, fill=X)

        frm_serial_config = Frame(lblfrm_serial_connection, bg="lightgray")
        frm_serial_config.pack(padx=4, pady=4, anchor="w", side=LEFT, fill=Y)
        lbl_port = Label(frm_serial_config, text="Port:", bg="lightgray")
        lbl_port.pack(padx=4, pady=4, side=LEFT)
        self.cbx_ports = ttk.Combobox(frm_serial_config, values=self.get_serial_ports())
        self.cbx_ports.pack(padx=4, pady=4, side=LEFT)
        self.cbx_ports.current(0)
        self.cbx_baud = ttk.Combobox(frm_serial_config, values=self.baudrates)
        self.cbx_baud.pack(padx=4, pady=4, side=LEFT)
        self.cbx_baud.current(0)
        frm_serial_connected = Frame(lblfrm_serial_connection, bg="lightgray")
        frm_serial_connected.pack(padx=4, pady=4, anchor="w", side=LEFT)
        frm_buttons = Frame(frm_serial_connected, bg="lightgray")
        frm_buttons.pack(padx=4, pady=4)
        Button(frm_buttons, text="Connect", command=self.start_serial).pack(padx=4, pady=4, side=LEFT)
        Button(frm_buttons, text="Disconnect", command=self.disconnect_serial).pack(padx=4, pady=4, side=LEFT)
        Label(frm_serial_connected, text="Serial:", bg="lightgray").pack(padx=4, pady=4, side=LEFT)
        self.lbl_serial_connected = Label(frm_serial_connected, width=8, bg="red")
        self.lbl_serial_connected.pack(padx=4, pady=4, side=LEFT)

        self.disableAll(lblfrm_serial_connection)

        # Steer pan tilt -----------------------------------------------------------------------------------------------
        lblfrm_pan_tilt = LabelFrame(self.master, text="Steer pan tilt")
        lblfrm_pan_tilt.pack(padx=4, pady=4, expand=True, fill=BOTH)

        # Steer cross
        frm_side_bar = Frame(lblfrm_pan_tilt, bg="darkgray")
        frm_side_bar.pack(padx=4, pady=4, anchor="e", expand=True, fill=Y, side=RIGHT)
        Label(frm_side_bar, textvariable=self.position_var).pack(padx=4, pady=4)
        frm_steer = Frame(frm_side_bar, bg="gray")
        frm_steer.pack(padx=4, pady=4)

        # Cross buttons
        btn_up = Button(frm_steer, text="↑", font=("Arial", 20))
        btn_up.bind('<ButtonPress-1>', self.up)
        btn_up.bind('<ButtonRelease-1>', self.stop)
        btn_up.grid(row=0, column=1)
        btn_left = Button(frm_steer, text="←", font=("Arial", 20))
        btn_left.bind('<ButtonPress-1>', self.left)
        btn_left.bind('<ButtonRelease-1>', self.stop)
        btn_left.grid(row=1, column=0)
        btn_right = Button(frm_steer, text="→", font=("Arial", 20))
        btn_right.bind('<ButtonPress-1>', self.right)
        btn_right.bind('<ButtonRelease-1>', self.stop)
        btn_right.grid(row=1, column=2)
        btn_down = Button(frm_steer, text="↓", font=("Arial", 20))
        btn_down.bind('<ButtonPress-1>', self.down)
        btn_down.bind('<ButtonRelease-1>', self.stop)
        btn_down.grid(row=2, column=1)

        # Scales
        self.h_slide = Scale(frm_side_bar, from_=0, to=180, orient=HORIZONTAL, command=self.horiz_changed)
        self.h_slide.pack()
        self.v_slide = Scale(frm_side_bar, from_=0, to=180, command=self.vertic_changed)
        self.v_slide.pack()

        # Video capture
        self.lbl_video = Label(lblfrm_pan_tilt)
        self.lbl_video.pack(padx=4, pady=4)
        # --------------------------------------------------------------------------------------------------------------

    def disableAll(self, parent):
        for child in parent.winfo_children():
            if len(child.winfo_children()) > 0:
                self.disableAll(child)
            try:
                child.configure(state='disabled')
            except Exception:
                pass

    def on_close(self):
        if self.serial_obj is not None:
            self.serial_obj.close()
        if self.camera is not None:
            self.camera.release()
        self.master.destroy()

    # Position ---------------------------------------------------------------------------------------------------------

    def stop(self, event):
        if self.job_id_cross is not None:
            self.master.after_cancel(self.job_id_cross)

    def update_position(self):
        self.position_var.set("[" + str(self.x) + ":" + str(self.y) + "]")
        self.h_slide.set(self.x)
        self.v_slide.set(self.y)

    def right(self, event):
        if self.x < 180:
            self.x += 1
            self.update_position()
            self.job_id_cross = self.master.after(200, self.right, 1)

    def left(self, event):
        if self.x > 0:
            self.x -= 1
            self.update_position()
            self.job_id_cross = self.master.after(200, self.left, 1)

    def up(self, event):
        if self.y > 0:
            self.y -= 1
            self.update_position()
            self.job_id_cross = self.master.after(200, self.up, 1)

    def down(self, event):
        if self.y < 180:
            self.y += 1
            self.update_position()
            self.job_id_cross = self.master.after(200, self.down, 1)

    def horiz_changed(self, event):
        self.x = self.h_slide.get()
        self.update_position()

    def vertic_changed(self, event):
        self.y = self.v_slide.get()
        self.update_position()

    # Connect/disconnect camera ----------------------------------------------------------------------------------------

    def connect(self):
        threading.Thread(target=self.start_camera, daemon=True).start()
        threading.Thread(target=self.start_tcp, daemon=True).start()

    def disconnect(self):
        self.tcp_connected = False
        if self.camera is not None:
            self.camera.release()
        self.lbl_vid_connected.config(bg="red")
        self.lbl_video.configure(image='')
        self.lbl_tcp_connected.config(bg='red')
        if self.job_id_frame is not None:
            self.master.after_cancel(self.job_id_frame)

    # TCP --------------------------------------------------------------------------------------------------------------
    def start_tcp(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
            try:
                self.lbl_tcp_connected.config(bg='orange')
                addr = (self.cam_ip_var.get(), int(self.tcp_port_var.get()))
                client.connect(addr)
                self.tcp_connected = True
                self.lbl_tcp_connected.config(bg='green')
                threading.Thread(target=self.update_tcp(client), daemon=True).start()
            except ConnectionError:
                self.tcp_connected = False
                self.lbl_tcp_connected.config(bg='red')

    def update_tcp(self, client):
        while True:
            try:
                new = self.position_var.get()
                old = self.position_old_var.get()
                if new != old:
                    self.position_old_var.set(new)
                    try:
                        client.send(bytes(new, "utf-8"))
                    except Exception:
                        pass
                if not self.tcp_connected:
                    break
            except KeyboardInterrupt:
                pass
            self.master.update()

    # Camera -----------------------------------------------------------------------------------------------------------
    def start_camera(self):
        try:
            self.lbl_vid_connected.config(bg='orange')
            self.camera = cv2.VideoCapture("http://" + self.cam_ip_var.get() + ":" + self.vid_port_var.get() + "/")
            if self.camera is None or not self.camera.isOpened():
                raise ConnectionError
            self.lbl_vid_connected.config(bg="green")
            self.show_frame()
        except ConnectionError:
            self.camera.release()
            self.lbl_vid_connected.config(bg="red")

    def show_frame(self):
        ret, frame = self.camera.read()
        if ret and frame is not None:
            frame = cv2.resize(frame, (self.lbl_video.winfo_width(), self.lbl_video.winfo_height()))
            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
            img = PIL.Image.fromarray(cv2image)
            imgtk = ImageTk.PhotoImage(image=img)
            self.lbl_video.imgtk = imgtk
            self.lbl_video.configure(image=imgtk)
            self.job_id_frame = self.master.after(10, self.show_frame)  # Needs to be with delay, because of flickering
        else:
            raise ConnectionError

    # Serial -----------------------------------------------------------------------------------------------------------
    def check_serial_port(self):
        if self.serial_obj.isOpen() and self.serial_obj.in_waiting:
            serial_input = self.serial_obj.readline().decode('utf-8').rstrip('\n')
            self.x = serial_input[serial_input.index('[') + 1:serial_input.index(':')]
            self.y = serial_input[serial_input.index(':') + 1:serial_input.index(']')]
            self.update_position()
        else:
            raise ConnectionError

    def update_serial(self):
        while True:
            try:
                if self.serial_obj.isOpen() and self.serial_obj.in_waiting:
                    serial_input = self.serial_obj.readline().decode('utf-8').rstrip('\n')
                    self.x = serial_input[serial_input.index('[') + 1:serial_input.index(':')]
                    self.y = serial_input[serial_input.index(':') + 1:serial_input.index(']')]
                    self.update_position()
            except Exception:
                self.lbl_serial_connected.config(bg="red")
                self.serial_obj.close()

    def start_serial(self):
        try:
            self.lbl_serial_connected.config(bg="orange")
            self.serial_obj = serial.Serial()
            self.serial_obj.port = self.get_serial_ports()[self.cbx_ports.current()]
            self.serial_obj.baudrate = self.baudrates[self.cbx_baud.current()]
            self.serial_obj.open()
            self.lbl_serial_connected.config(bg="green")
            threading.Thread(target=self.update_serial, daemon=True).start()
        except ConnectionError:
            self.lbl_serial_connected.config(bg="red")
            self.serial_obj.close()

    def disconnect_serial(self):
        self.lbl_serial_connected.config(bg="red")
        self.serial_obj.close()

    def get_serial_ports(self):
        ports = serial.tools.list_ports.comports()
        portVars = [len(ports)]

        for i in range(len(ports)):
            portVars[i] = str(ports[i]).split(' ')[0]
        return portVars

    def update_serial_ports(self):
        new_ports = list(self.get_serial_ports())
        self.cbx_ports['values'] = new_ports

        self.master.after(1000, self.update_serial_ports)


if __name__ == '__main__':
    root = Tk()
    gui = FancyGUI(root)
    root.mainloop()
    sys.exit()
