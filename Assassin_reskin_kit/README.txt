ASSASSIN RE-SKIN KIT (made by source/tools/make_reskin_kit.py: a copy, rebuilt whenever a prompt, a guide or the reference picture changes).

One folder per animation. Every folder holds everything for one generation: the look's reference picture, the pose guide(s), and the prompt file(s).
To generate: attach reference_image.png and the guide named in the prompt (guide_sheet_1.png, or guide_uidNN.png for one pose), paste the prompt file's text, ask for the picture size the prompt says;
save the result in the project's inbox/ folder with the name the prompt says, and tell Claude.

01_idle: 6 idle poses (DONE: the sheet was used; the single-image prompt is the alternative)
   files: guide_sheet_1.png, guide_uid00.png, guide_uid05.png, prompt_sheet.txt, prompt_single_one_pose_at_a_time.txt, reference_image.png
02_permafrost_execution: sheet of 6 + the retreat as a single image (DONE)
   files: guide_sheet_1.png, guide_sheet_2.png, guide_uid06.png, prompt_sheet.txt, prompt_single_retreat.txt, reference_image.png
03_run: 6 run poses (DONE)
   files: guide_sheet_1.png, prompt_sheet.txt, reference_image.png
04_hit: 6 hit poses (DONE)
   files: guide_sheet_1.png, prompt_sheet.txt, reference_image.png
05_death: 6 death poses (DONE)
   files: guide_sheet_1.png, prompt_sheet.txt, reference_image.png
06_dodge: 6 dodge poses (DONE; the hop frames 3-4 are the weakest)
   files: guide_sheet_1.png, prompt_sheet.txt, reference_image.png
07_shadow_shiv: 3 poses (DONE; the Static Stiletto only re-uses its stab frame)
   files: guide_sheet_1.png, prompt_sheet.txt, reference_image.png
08_umbral_shroud: 6 poses (DONE)
   files: guide_sheet_1.png, prompt_sheet.txt, reference_image.png
09_abyssal_backstab: 5 TALL poses, in the air (BUILT from the vertical sheet as a test; regenerate if the emerge or the strike frame looks wrong)
   files: guide_sheet_1.png, prompt_sheet.txt, reference_image.png
10_winters_kiss: 5 poses; only pose 5 (the catch) is to be REDRAWN as a single image: the wrong arm catches. prompt_single_pose5_REDRAW_catch.txt + ref_uid04.png (+ reference_image.png). Poses 1-4 are fine (pose 4 was redone earlier).
   files: guide_sheet_1.png, prompt_sheet.txt, prompt_single_pose5_REDRAW_catch.txt, ref_uid04.png, reference_image.png
11_static_stiletto: 6 poses, 3:2 (DONE 2026-11-06: the sheet came out right first time; the Rogue's Spark Streak Stab version; its stab frame comes from the Shadow Shiv, its last frame from the idle; panel 5 is in the air)
   files: guide_sheet_1.png, prompt_sheet.txt, reference_image.png
