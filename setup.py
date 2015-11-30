import cx_Freeze

executables = [cx_Freeze.Executable("anisi_dist.py")]

cx_Freeze.setup(
    name="Ani_SpaceInvaders",
    options={"build_exe":{"packages":["pygame"],"include_files":['data/']}},
    description = "Space Invaders by Ani",
    author= "Ani Tangellapalli",
    executables = executables
)