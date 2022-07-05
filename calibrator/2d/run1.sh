extri=./extrinsic
intri=./intrinsic

mv ~/*.mp4 ./extrinsic/videos

python3 ../../human_reconstructor/easymocap/scripts/preprocess/extract_video.py ${extri} --no2d
