# UROP-World-Model
This is my UROP project

Here, I provide some command, so that you can easily copy and paste it. (run in your terminal)

```
python 1_vlm_demo.py --demo_path ./demo --save_part_ply True --remove_bg False --ckpt ./pretrain/vlm
```
``` 
python 2_decoder.py
```
```
python 3_split.py
```
```
python 4_simready_gen.py --voxel_define 32 --basepath ./test_demo --process 0 --fixed_base 0 --deformable 0
```