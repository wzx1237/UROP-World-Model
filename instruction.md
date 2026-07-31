我现在要搭建一个pipeline, 实现Picture (text) 2 Vedio的生成 (input: picture and text; output: vedio, mp4格式)。我们的计划是：
1. 输入的图片为png格式，已经去除背景，放在一个叫做inputs的folder中。
2.使用PhysX-Anything的mesh generate功能生成一个可用的urdf格式的mesh, 生成好的mesh放在一个叫meshes的folder中。
3. MoReGen使用生成好的mesh来生成视频，结果就放在一个叫results的folder中. 

file structure:
base
    /MoReGen
      /output_frames
        images... (在原本的MoReGen pipeline中，result在这里)
      prompts.txt (input text放在这里)
      /qwen_coder_agent
        /reference
          pybullet_reference.md
        pybullet_modules.txt
        run_coder.py
      /result (存储生成的code, 而不是vedio)
      manim_agent.py
      vlm_agent.py

    /PISA   (for evaluation use, ignore it please)
    /PhysX-Anything
        /demo
          demo1.png
        /test_demo (在原来的pipeline中结果会出现在这里)
        1_vlm_demo.py
        2_decoder.py
        3_split.py
        4_simready_gen.py

    inputs (把那个图片输入放在这里就行，我会把txt放对地方的)
    meshes
    results (结果放在这里)

(Note: 我只给出了部分文件的directory, 因为我认为你只会用到这些file)

注意事项：
1. 在UROP-World-Model这个folder下，我会开一个名叫test_pipeline的folder. 请把你写的所有code都放到这个folder里
2. PhysX-Anything的virtual environment和MoReGen是不同的，它们的environment分别叫做: physx-anything和MoReGen
3. 我不会在GitHub的repo里面进行调试。你只需要把需要的代码写道repo里面就行。(repo里面不会有MoReGen和physx的代码，你写不用把它们pull下来。我想在放进repo前先在我的虚拟机上调试好再说)
4. 虚拟机的环境是Linux. 在开新的terminal之前记得先激活bash，因为我没有调整tcsh的config file, 导致在tcsh里面没有conda
