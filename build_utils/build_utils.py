import os
import subprocess
import shutil
import fileinput

def clone_and_build( build_dir, output_lib_path):
    return
    """
    Clone a Git repository and build a shared library.
    """
    my_env = os.environ.copy()
    my_env["CFLAGS"] = f"-fPIC -fvisibility=default -O2"
    my_env["CXXFLAGS"] = f"{my_env['CFLAGS']}"
    enable=False
    rebuild_uade=True
    reconfigure_uade=False
    audacious_uade_dir = os.path.join(build_dir, 'audacious-uade')

    if rebuild_uade:
        audacious_repo_url="https://github.com/mvtiaine/audacious-uade"
        if not os.path.exists(audacious_uade_dir):
            print(f"Cloning repository: {audacious_repo_url}")
            subprocess.check_call(["git", "clone",audacious_repo_url , audacious_uade_dir, "--recursive"])
        else:
            print(f"Repository already exists at: {audacious_uade_dir}")
        shutil.copy("../audacious-uade-extras/player.cc", os.path.join(audacious_uade_dir, 'src/plugin/cli/player/'))
        shutil.copy("../audacious-uade-extras/precalc.cc", os.path.join(audacious_uade_dir, 'src/plugin/cli/precalc/'))
        print("Change to audacious-uade directory...")
        print("Patching src/plugin/cli/Makefile.am.inc ...")
        os.chdir(os.path.join(audacious_uade_dir, 'src/plugin/cli/'))
        with fileinput.FileInput("Makefile.am.inc", inplace=True) as file:
            for line in file:
                print(line.replace("plugin_cli_player_player_SOURCES = \\", "plugin_cli_player_player_SOURCES =  \\\n plugin/cli/player/player.cc \\"), end='')
        with fileinput.FileInput("Makefile.am.inc", inplace=True) as file:
            for line in file:
                print(line.replace("plugin_cli_precalc_precalc_SOURCES = \\", "plugin_cli_precalc_precalc_SOURCES =  \\\n plugin/cli/precalc/precalc.cc \\"), end='')
        # Run autotools commands
        os.chdir(audacious_uade_dir)
        if reconfigure_uade:
            print("Running libtoolize...")
            subprocess.check_call(["libtoolize"])
            print("Running autoreconf -i...")
            subprocess.check_call(["autoreconf", "-i"])
        print("Creating audacious-uade build directory...")
        os.makedirs("../build", exist_ok=True)
        print("Change to audacious-uade build directory...")
        os.chdir("../build")
        if reconfigure_uade:
            print("Running configure...")
            subprocess.check_call(["../configure"], env=my_env)
        # Build the shared library
        print("Building audacious-uade ...")
        if reconfigure_uade:
            subprocess.check_call(["make","clean"])
        subprocess.check_call(["make"])

    my_env2 = os.environ.copy()
    my_env2["CFLAGS"] = f"-fPIC -fvisibility=default -O2"
    my_env2["CXXFLAGS"] = f"{my_env['CFLAGS']}"

    #get/compile libxmp
    if enable:
        libxmp_repo_url = "https://github.com/libxmp/libxmp"
        libxmp_dir = os.path.join(build_dir, 'libxmp')
        if not os.path.exists(libxmp_dir):
            os.makedirs(libxmp_dir, exist_ok=True)
            print(f"Cloning repository: {libxmp_repo_url}")
            subprocess.check_call(["git", "clone", libxmp_repo_url, libxmp_dir])
        else:
            print(f"Repository already exists at: {libxmp_dir}")
        os.chdir(libxmp_dir)
        subprocess.check_call(["./autogen.sh"])
        subprocess.check_call( "./configure --enable-static" , env=my_env2,shell=True)
        subprocess.check_call(["make","clean"])
        subprocess.check_call(["make"])


    #get/compile libopenmpt
    libopenmpt_version = "libopenmpt-0.7.13+release.autotools"
    if enable:
        libopenmpt_url = "https://lib.openmpt.org/files/libopenmpt/src/libopenmpt-0.7.13+release.autotools.tar.gz"
        libopenmpt_dir = os.path.join(build_dir, 'libopenmpt')
        os.makedirs(libopenmpt_dir, exist_ok=True)
        os.chdir(libopenmpt_dir)
        print(f"downloading: {libopenmpt_url}")
        if not os.path.exists("./"+libopenmpt_version+".tar.gz"):
            subprocess.check_call(["wget",libopenmpt_url])
        if not os.path.exists("./"+libopenmpt_version):
            subprocess.check_call(["tar", "-xzvf", "./"+libopenmpt_version+".tar.gz"])
        os.chdir("./"+libopenmpt_version)
        subprocess.check_call(["autoconf","-i"])
        os.chdir("../build")
        subprocess.check_call("../configure --enable-static --without-mpg123 --without-ogg --without-vorbis --without-vorbisfile", env=my_env2,shell=True)
        subprocess.check_call(["make","clean"])
        subprocess.check_call(["make"])

    os.chdir(os.path.join(audacious_uade_dir, 'build'))


    if True:
        subprocess.check_call(
            "gcc -shared -Wl,--exclude-libs=ALL -Wl,--gc-sections -Wl,--discard-all  -o " + output_lib_path +
            " ./src/plugin/cli/precalc/precalc.o ./src/plugin/cli/player/player.o  "
            "./src/songend/.libs/libsongend.a ./src/songdb/.libs/libsongdb.a ./src/common/.libs/libmd5.a "
            "./uade/src/frontends/common/libuade.a ../../libxmp/lib/libxmp.a ../../libopenmpt/"
            +libopenmpt_version+"/build/.libs/libopenmpt.a ./src/plugin/cli/common/logger.o -lstdc++ ",
            shell=True)

    print(f"Shared library written to: {output_lib_path}")
    os.chdir(os.path.join(build_dir, '../'))
