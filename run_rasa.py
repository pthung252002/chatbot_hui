import subprocess
import time

# Đường dẫn thư mục dự án Rasa
rasa_project_path = "E:\\chatbot_rasa"

# Lệnh chạy Action Server
command_actions = f'start cmd /k "cd /d {rasa_project_path} && rasa run actions"'

# Lệnh chạy Rasa Server
command_rasa = f'start cmd /k "cd /d {rasa_project_path} && rasa run --enable-api --cors \"*\" --debug"'

# Mở Terminal 1 - Chạy Action Server
subprocess.run(command_actions, shell=True)

# Đợi 5 giây để Action Server khởi động trước khi chạy Rasa Server
time.sleep(5)

# Mở Terminal 2 - Chạy Rasa Server
subprocess.run(command_rasa, shell=True)

print("✅ Hai terminal đã được mở và các lệnh đang chạy!")
