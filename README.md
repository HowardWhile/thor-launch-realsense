# thor-launch-realsense


## 環境需求

- Python 3 與 ROS 2。
- ROS 2 的 `realsense2_camera` 套件。
- 提供 `rs-enumerate-devices` 指令的 `librealsense2-utils`。
- 已連接且可被系統辨識的 RealSense 相機。

在已載入 ROS 2 環境的終端機中，可使用下列指令安裝相機相關套件（套件是否可用取決於作業系統與 ROS 發行版）：

```bash
sudo apt install ros-${ROS_DISTRO}-realsense2-camera librealsense2-utils
```

若找不到 `librealsense2-utils`，請依照 [RealSense Linux 安裝說明](https://github.com/realsenseai/librealsense/blob/master/doc/distribution_linux.md) 設定套件來源。

## 使用方式

先執行以下指令，載入 ROS 2 Jazzy 環境：

```bash
source /opt/ros/jazzy/setup.bash
```

在本專案目錄執行：

```bash
ros2 launch ./launch_realsense.py
```

第一台相機立即啟動，其餘相機預設每隔 2 秒啟動一台。可用 `interval` 調整間隔（單位為秒，接受非負有限數值，包含小數；`0` 表示不延遲）：

```bash
ros2 launch ./launch_realsense.py interval:=5
```

按 `Ctrl+C` 停止所有相機。若未偵測到相機、缺少依賴套件或裝置列舉失敗，腳本會回報錯誤。

## 授權

本專案採用 [MIT License](LICENSE)。
