from pyamigamods.precalc import precalc_mod

def print_module(module):
    if module.exit_value == 1:
        print("error")
        print(module.error_msg)
    else:
        print("success")
        print(
            module.md5 + " " + str(module.size) + " " + str(
                module.nb_subsongs) + " " +
                module.player + " " + str(module.channels) + " " + module.format)
        for i in range(module.nb_subsongs):
            print(module.subsongs[i].status + " " + str(module.subsongs[i].index) + " " + str(
                module.subsongs[i].length))

#module=precalc_mod('./mods/hybris.fp')

#module=precalc_mod('./mods/burgertime mix.xm')
#print_module(module)

module=precalc_mod('./mods/mod.ORIENTALEV4.CHIP')
print_module(module)

#failure
#module=precalc_mod('./mods/astaroth-game.ymst')

#module=precalc_mod('./mods/STK.bowlstheme')

#libxmp
#module=precalc_mod('./mods/silly venture.mgt')

#libopenmpt
#module=precalc_mod('./mods/starport bbs introtune.s3m')

