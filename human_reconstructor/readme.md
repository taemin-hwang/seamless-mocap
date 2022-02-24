# Human Reconstructor
This program reconstruct a realistic 3D model of the human body with 2D human keypoints.


## pre-requisite
```
pip install opencv-python IPython matplotlib scipy
```

## clone repository
```
git clone --recursive https://github.com/taemin-hwang/seamless-mocap.git
```

## run
### gui
We use visualization tool of EasyMocap project. Please refer to the below site.
<https://github.com/zju3dv/EasyMocap/blob/master/doc/realtime_visualization.md>

```
# Start the server for basic skeletons
run_gui.sh
```

```
# Start the server for SMPL
run_gui.sh -smpl
```

### app
```
run_app.sh
```
### test

```
run_app.sh -smpl
```