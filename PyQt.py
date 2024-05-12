import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget, QLabel, QStackedWidget, QGridLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPixmap
from functools import partial
import sys
import os
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtCore import QUrl
import paramiko
from io import StringIO
from matplotlib.font_manager import FontProperties
# 设置支持中文的字体
font = FontProperties(fname="C:/Windows/Fonts/simhei.ttf", size=14)

import socket
import threading

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('172.20.10.3', 5000))
server_socket.listen(10)

print("服务器已启动，等待客户端连接...")

def run_remote_command(hostname, port, username, password, command):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(hostname, port=port, username=username, password=password)
        stdin, stdout, stderr = client.exec_command(command)
        output = stdout.read().decode()
        return output
    except paramiko.AuthenticationException:
        print("Authentication failed.")
    except paramiko.SSHException as e:
        print("SSH connection failed:", str(e))
    finally:
        client.close()

class AppWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BeeLab智能电梯")
        self.resize(800, 600)  # 设置窗口的初始大小

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # Sidebar buttons
        sidebar_layout = QVBoxLayout()
        sidebar_widget = QWidget(self)
        sidebar_widget.setLayout(sidebar_layout)

        live_button = QPushButton("实时监控")
        retrieval_button = QPushButton("监控调取")
        alert_button = QPushButton("发送警告")
        chart_button = QPushButton("数据分析")  # New button for generating charts
        preview_button = QPushButton("效果展示")

        # 设置按钮的样式
        button_style = '''
            QPushButton {
                background-color: #4CAF50;  /* 设置背景颜色 */
                color: white;  /* 设置文本颜色 */
                border: none;  /* 不显示边框 */
                border-radius: 5px;  /* 设置圆角 */
                padding: 10px 20px;  /* 设置内边距 */
            }
            QPushButton:hover {
                background-color: #45a049;  /* 设置鼠标悬停时的背景颜色 */
            }
            QPushButton:pressed {
                background-color: #3e8e41;  /* 设置按钮按下时的背景颜色 */
            }
        '''

        live_button.setStyleSheet(button_style)
        retrieval_button.setStyleSheet(button_style)
        alert_button.setStyleSheet(button_style)
        chart_button.setStyleSheet(button_style)
        preview_button.setStyleSheet(button_style)

        sidebar_layout.addWidget(live_button)
        sidebar_layout.addWidget(retrieval_button)
        sidebar_layout.addWidget(alert_button)
        sidebar_layout.addWidget(chart_button)  # Add the chart button to the sidebar
        sidebar_layout.addWidget(preview_button)

        # Right-side main page with video playback area
        main_page = QWidget(self)
        main_layout = QVBoxLayout()
        main_page.setLayout(main_layout)

        video_label = QLabel("Video Playback Area")
        video_label.setAlignment(Qt.AlignCenter)  # Align the label text to the center
        main_layout.addWidget(video_label)

        # Create a video playback area
        self.video_widget = QVideoWidget(self)
        main_layout.addWidget(self.video_widget)

        # Stacked widget for switching between pages
        self.stacked_widget = QStackedWidget(central_widget)
        self.stacked_widget.addWidget(main_page)
        self.stacked_widget.addWidget(self.video_widget)  # Add the video widget to the stacked widget

        central_layout = QHBoxLayout()
        central_layout.addWidget(sidebar_widget)
        central_layout.addWidget(self.stacked_widget)

        central_widget.setLayout(central_layout)

        # Connect button signals to slots
        live_button.clicked.connect(self.live_video)
        retrieval_button.clicked.connect(self.show_date_list)
        alert_button.clicked.connect(self.send_alert_message)
        chart_button.clicked.connect(self.generate_charts)  # Connect the chart button to the generate_charts method
        preview_button.clicked.connect(self.show_preview)

        # Create media player
        self.media_player = QMediaPlayer(self)
        self.media_player.setVideoOutput(self.video_widget)

    def show_date_list(self):
        self.stop_video()
        # Method to show the date list and play the selected video
        date_list = ["2023-07-01", "2023-07-02", "2023-07-03", "2023-07-04"]  # Predefined date list

        date_list_widget = QListWidget(self)
        date_list_widget.addItems(date_list)
        date_list_widget.itemClicked.connect(partial(self.play_video, date_list_widget))
        self.stacked_widget.addWidget(date_list_widget)
        self.stacked_widget.setCurrentWidget(date_list_widget)

    def live_video(self):
        def live_thread():
            command_output = run_remote_command('192.168.1.10', 22, 'sunrise', 'sunrise', 'echo "sunrise" | sudo -S python3 /home/sunrise/Documents/camera/mipi_camera.py')
        thread = threading.Thread(target=live_thread)
        thread.start()

    def play_video(self, date_list_widget, item):
        # Method to play the selected video
        selected_date = item.text()
        video_path = f"{selected_date}.mp4"  # Construct the video file path

        media_content = QMediaContent(QUrl.fromLocalFile(video_path))
        self.media_player.setMedia(media_content)
        self.media_player.play()

        # Show the video widget
        self.stacked_widget.setCurrentWidget(self.video_widget)

    def generate_charts(self):
        self.stop_video()
        # Method to generate and display the charts in the right-side main page
        x = np.linspace(0, 10, 100)
        # 使用随机数据创建曲折上升和曲折下降的折线
        y1 = np.abs(np.cumsum(np.random.rand(100) - 0.5)*1000)
        y2 = np.abs(np.cumsum(np.random.rand(100) - 0.5)*1000)
        y3 = np.abs(np.cumsum(np.random.rand(100) - 0.5)*10)
        y4 = np.abs(np.cumsum(np.random.rand(100) - 0.5)*10)
        data = np.random.normal(size=100)

        fig1 = Figure(figsize=(5, 3))
        ax1 = fig1.add_subplot(111)
        ax1.plot(x, y1, label='小区a')
        ax1.plot(x, y2, label='小区b')
        ax1.set_title("电梯客流量",fontproperties=font)
        ax1.legend(prop=font)

        fig2 = Figure(figsize=(5, 3))
        ax2 = fig2.add_subplot(111)
        ax2.plot(x, y3, label='小区a')
        ax2.plot(x, y4, label='小区b')
        ax2.set_title("检测到电瓶车次数",fontproperties=font)
        ax2.legend(prop=font)

        fig3 = Figure(figsize=(5, 3))
        ax3 = fig3.add_subplot(111)
        bins = np.arange(0, int(np.ceil(np.max(data))) + 1, 1)
        ax3.hist(data, bins=bins)
        ax3.set_title("入梯离开时长",fontproperties=font)

        fig4 = Figure(figsize=(5, 3))
        ax4 = fig4.add_subplot(111)
        data_table = np.array([
            ['小区a', 35, 1],
            ['小区d', 33, 2],
            ['小区c', 25, 3],
            ['小区e', 22, 4],
            ['小区b', 17, 5],
            ['小区g', 7, 6],
            ['小区f', 4, 7]
        ], dtype=object)
        ax4.axis('off')
        table = ax4.table(cellText=data_table, colLabels=['A', 'B', 'C', 'D', 'E'], loc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 1.5)
        ax4.set_title("小区电瓶车进楼统计排行",fontproperties=font)
        for key, cell in table.get_celld().items():
            cell.set_text_props(fontproperties=font)

        # Create a QGridLayout and add all four charts to it
        charts_layout = QGridLayout()
        charts_layout.addWidget(FigureCanvas(fig1), 0, 0)
        charts_layout.addWidget(FigureCanvas(fig2), 0, 1)
        charts_layout.addWidget(FigureCanvas(fig3), 1, 0)
        charts_layout.addWidget(FigureCanvas(fig4), 1, 1)

        # Set the QGridLayout as the layout for the main page widget
        main_page = QWidget()
        main_page.setLayout(charts_layout)

        # Add the main page widget to the stacked widget
        self.stacked_widget.addWidget(main_page)
        self.stacked_widget.setCurrentWidget(main_page)

    def stop_video(self):
        # Method to stop video playback if currently playing
        if self.media_player.state() == QMediaPlayer.PlayingState:
            self.media_player.stop()
            self.stacked_widget.setCurrentWidget(self.stacked_widget.currentWidget())

    def send_alert_message(self):
        def server_threading():
            while True:
                client_socket, client_address = server_socket.accept()
                print("客户端已连接：", client_address)

                message = "警告！有电瓶车进入电梯！！"
                client_socket.send(message.encode('utf-8'))
                client_socket.close()
        
        thread = threading.Thread(target=server_threading)
        thread.start()


    def show_preview(self):
        # Method to show the preview image and display the execution result
        self.stop_video()

        # Load and display the preview image
        preview_image_path = os.path.join(os.path.dirname(__file__), "preview.png")
        preview_label = QLabel(self)

        # Get the size of the right-side main window
        main_page_size = self.stacked_widget.currentWidget().size()

        # Load the preview image and resize it to fit the size of the main window
        preview_pixmap = QPixmap(preview_image_path)
        preview_pixmap = preview_pixmap.scaled(main_page_size, Qt.AspectRatioMode.KeepAspectRatio, Qt.SmoothTransformation)
        preview_label.setPixmap(preview_pixmap)
        preview_label.setAlignment(Qt.AlignCenter)

        # Create a layout for the main page widget
        main_page_layout = QVBoxLayout()
        main_page_layout.addWidget(preview_label)

        # Execute the remote command and get the output
        command_output = run_remote_command('192.168.1.10', 22, 'sunrise', 'sunrise', 'echo "sunrise" | sudo -S python3 /home/sunrise/Documents/x3pcodes/inference_model_bpu1.py')

        # Add the execution result label to the layout
        result_label = QLabel(f"执行结果: {command_output}", self)
        result_label.setAlignment(Qt.AlignCenter)
        main_page_layout.addWidget(result_label)

        # Create the main page widget and set the layout
        main_page = QWidget()
        main_page.setLayout(main_page_layout)

        # Add the main page widget to the stacked widget
        self.stacked_widget.addWidget(main_page)
        self.stacked_widget.setCurrentWidget(main_page)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AppWindow()
    window.show()
    app.exec_()
