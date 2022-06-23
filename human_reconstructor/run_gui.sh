pushd easymocap

if [ $# -eq 0 ]; then
  python3 apps/vis/vis_server.py --cfg config/vis3d/o3d_scene.yml
else
  if [ $1 == "-smpl" ]; then
    python3 apps/vis/vis_server.py --cfg config/vis3d/o3d_scene_smpl.yml write True out ../output/mesh-smpl camera.cz 3. camera.cy 0.5
  fi
  if [ $1 == "-mvmp" ]; then
    python3 apps/vis/vis_server.py --cfg config/vis3d/o3d_scene.yml write True out ../output/skel-multi camera.cz 3. camera.cy 0.5
  fi
fi

if [ $# -eq 2 ]; then
  python3 apps/vis/vis_server.py --cfg config/vis3d/o3d_scene.yml host $1 port $2
fi

popd
