extri=./extrinsic
intri=./intrinsic

python3 ../../human_reconstructor/easymocap/apps/calibration/detect_chessboard.py ${extri} --out ${extri}/output/calibration --pattern 10,7 --grid 0.30
