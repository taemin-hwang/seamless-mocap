This program reconstruct a realistic 3D model of the human body with 2D human keypoints.


# 1. clone repository
Clone this repository including submodules from EasyMocap
```
git clone --recursive https://github.com/taemin-hwang/seamless-mocap.git
```

# 2. Run
## 2-1. Run Visualizer
We use visualization tool of EasyMocap project. Please refer to the below site.
<https://github.com/zju3dv/EasyMocap/blob/master/doc/realtime_visualization.md>

```
# Start the server for 3D keypoints
run_gui.sh
```

```
# Start the server for SMPL
run_gui.sh -smpl
```

## 2-2. Run App
### 2-2-1. Usage
```
usage: main.py [-h] -p PATH [-v] [-s] [-k]

Reconstruct 3D pose and shape with SMPL model

optional arguments:
  -h, --help            show this help message and exit
  -p PATH, --path PATH  Path for config.json
  -v, --visual          Enable 2D visualizer
  -s, --smpl            Reconstruct shape with SMPL
  -k, --keypoint        Reconstruct 3D keypoint wihtout SMPL
```

### 2-2-2. Example
```
main.py -p <config path> -vs # Reconstruct 3D keypoints with visualizer
run_app.sh -vs # Use shell script with default ./etc/ path 
```
