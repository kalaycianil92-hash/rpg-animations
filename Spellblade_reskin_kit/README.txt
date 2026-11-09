SPELLBLADE RE-SKIN KIT (made by source/tools/make_reskin_kit.py: a copy, rebuilt whenever a prompt, a guide or the reference picture changes).

One folder per animation. Every folder holds everything for one generation: the look's reference picture, the pose guide(s), and the prompt file(s).
To generate: attach reference_image.png and the guide named in the prompt (guide_sheet_1.png, or guide_uidNN.png for one pose), paste the prompt file's text, ask for the picture size the prompt says;
save the result in the project's inbox/ folder with the name the prompt says, and tell Claude.

01_idle: 6 idle poses
   files: guide_sheet_1.png, guide_uid00.png, guide_uid05.png, prompt_sheet.txt, prompt_single_one_pose_at_a_time.txt, reference_image.png
02_permafrost_execution: sheet of 6 + the retreat as a single image (the eighth image of the animation is the idle's first frame: nothing to draw)
   files: guide_sheet_1.png, guide_sheet_2.png, guide_uid06.png, prompt_sheet.txt, prompt_single_retreat.txt, reference_image.png
03_run: 6 run poses
   files: guide_sheet_1.png, prompt_sheet.txt, reference_image.png
04_hit: 6 hit poses
   files: guide_sheet_1.png, prompt_sheet.txt, reference_image.png
05_death: 6 death poses
   files: guide_sheet_1.png, prompt_sheet.txt, reference_image.png
06_dodge: 6 dodge poses
   files: guide_sheet_1.png, prompt_sheet.txt, reference_image.png
07_shadow_shiv: 3 poses
   files: guide_sheet_1.png, prompt_sheet.txt, reference_image.png
08_umbral_shroud: 6 poses
   files: guide_sheet_1.png, prompt_sheet.txt, reference_image.png
09_abyssal_backstab: 5 TALL poses, in the air: ask for a SQUARE 1:1 image (the Assassin's came out as a vertical sheet; that still worked, tell me what you got)
   files: guide_sheet_1.png, prompt_sheet.txt, reference_image.png
10_winters_kiss: 5 poses. Use the sheet for poses 1-3, and draw poses 4 and 5 as SINGLE images (they went wrong in the Assassin's sheet: the head angle of pose 4, the wrong arm catching in pose 5): prompt_single_pose4_rogue_reference.txt + ref_uid03.png, and prompt_single_pose5_REDRAW_catch.txt + ref_uid04.png (each with reference_image.png). If the sheet's panels 4 and 5 come out right, the singles are not needed.
   files: guide_sheet_1.png, prompt_sheet.txt, prompt_single_pose4_rogue_reference.txt, prompt_single_pose5_REDRAW_catch.txt, ref_uid03.png, ref_uid04.png, reference_image.png
11_static_stiletto: 6 poses, 3:2 (panel 5 is in the air; its stab frame comes from the Shadow Shiv, its last frame from the idle)
   files: guide_sheet_1.png, prompt_sheet.txt, reference_image.png
