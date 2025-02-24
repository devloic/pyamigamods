from pyamigamods.precalc import precalc_mod

def print_module(module):
    import cffi
    ffi = cffi.FFI()
    print(
        module.md5 + " " + str(module.size) + " " + str(
            module.nb_subsongs) + " " +
            module.player + " " + str(module.channels) + " " + module.format)
    for i in range(module.nb_subsongs):
        print(module.subsongs[i].status + " " + str(module.subsongs[i].index) + " " + str(
            module.subsongs[i].length))

#module=precalc_mod('/home/lolo/mnt/WDBLACK/amiga/mods/futurecomposer/audacious-uade/testdata/burgertime mix.xm')
#module=precalc_mod('/home/lolo/docker_apps/mvtiane/audacious-uade/testlolo/hybris.fp')
#module=precalc_mod('/home/lolo/docker_apps/mvtiane/audacious-uade/testdata/starport bbs introtune.s3m')
#module=precalc_mod('/home/lolo/docker_apps/mvtiane/audacious-uade/testdata/burgertime mix.xm')
#module=precalc_mod('/home/lolo/docker_apps/mvtiane/audacious-uade/testdata/silly venture.mgt')
#module=precalc_mod('/home/lolo/docker_apps/mvtiane/audacious-uade/testlolo/astaroth-game.ymst')
#module=precalc_mod('/home/lolo/Téléchargements/amiga/mods/STK.bowlstheme')

#libxmp
module=precalc_mod('/home/lolo/docker_apps/mvtiane/audacious-uade/testdata/silly venture.mgt')
#libopenmpt
#module=precalc_mod('/home/lolo/docker_apps/mvtiane/audacious-uade/testdata/starport bbs introtune.s3m')
#module=precalc_mod('/home/lolo/docker_apps/mvtiane/audacious-uade/testdata/burgertime mix.xm')

if module.exit_value==1:
    print(module.error_msg)
else:
    print("module")
    print_module(module)