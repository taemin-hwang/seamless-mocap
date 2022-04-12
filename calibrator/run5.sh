extri=./extrinsic
intri=./intrinsic

python3 ../human_reconstructor/easymocap/apps/calibration/check_calib.py ${extri} --out ${intri}/output --cube
