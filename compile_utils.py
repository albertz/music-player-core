
from __future__ import print_function
import os
import sys
from subprocess import check_output, CalledProcessError


def sys_exec(cmd):
    print(" ".join(cmd))
    r = os.system(" ".join(cmd))
    if r != 0:
        sys.exit(r)


def is_uptodate(outfile, depfiles=None):
    try:
        outmtime = os.path.getmtime(outfile)
    except OSError:
        return False
    if depfiles is None:
        try:
            depfiles = get_depfiles(outfile)
        except IOError:
            return False
    for depfn in depfiles:
        try:
            if os.path.getmtime(depfn) > outmtime:
                return False
        except OSError:
            return False
    return True


def get_cc_outfilename(infile):
    # Kind of custom, not totally bullet-proof, but it's ok
    # for our most common input, like "../musicplayer.cpp".
    fn = os.path.splitext(infile)[0]
    if fn.startswith("../"):
        fn = fn[3:]
    else:
        fn = "++" + fn
    fn = fn.replace("/", "+_")
    fn = fn.replace("..", "+.")
    return fn + ".o"


def get_depfilename(outfile):
    return outfile + ".deps"


def get_depfiles(outfile):
    depfile = get_depfilename(outfile)
    first_line = True
    lastLine = False
    fileList = []
    for line in open(depfile):
        line = line.strip()
        if not line: continue
        assert not lastLine
        if first_line:
            assert line.startswith(outfile + ": ")
            line = line[len(outfile) + 2:]
            first_line = False
        if line[-2:] == " \\":
            line = line[:-2]
        else:
            lastLine = True
        fileList += line.split()
    assert lastLine
    return fileList


def get_mtime(filename):
    return os.path.getmtime(filename)


LDFLAGS = os.environ.get("LDFLAGS", "").split()


def link(outfile, infiles, options):
    if "--weak-linking" in options:
        idx = options.index("--weak-linking")
        options[idx:idx + 1] = ["-undefined", "dynamic_lookup"]

    if is_uptodate(outfile, depfiles=infiles):
        print("up-to-date:", outfile)
        return

    if sys.platform == "darwin":
        sys_exec(
            ["libtool", "-dynamic", "-o", outfile] +
            infiles +
            options +
            LDFLAGS +
            ["-lc"]
        )
    else:
        sys_exec(
            ["ld"] +
            ["-L/usr/local/lib"] +
            infiles +
            options +
            LDFLAGS +
            ["-lc"] +
            ["-shared", "-o", outfile]
        )


def link_exec(outfile, infiles, options):
    options += ["-lc", "-lc++"]

    if is_uptodate(outfile, depfiles=infiles):
        print("up-to-date: %s" % outfile)
        return

    sys_exec(
        ["cc"] +
        infiles +
        options +
        LDFLAGS +
        ["-o", outfile]
    )


CFLAGS = os.environ.get("CFLAGS", "").split()
CFLAGS += ["-fpic"]


def cc_single(infile, options):
    options = list(options)
    ext = os.path.splitext(infile)[1]
    if ext in [".cpp", ".mm"]:
        options += ["-std=c++11"]

    outfilename = get_cc_outfilename(infile)
    depfilename = get_depfilename(outfilename)

    if is_uptodate(outfilename):
        print("up-to-date: %s" % outfilename)
        return

    sys_exec(
        ["cc"] + options + CFLAGS +
        ["-c", infile, "-o", outfilename, "-MMD", "-MF", depfilename]
    )


def cc(files, options):
    for f in files:
        cc_single(f, options)


LinkPython = False
UsePyPy = False
Python3 = True

ffmpeg_packages = ['libavutil', 'libavformat', 'libavcodec', 'libswresample']


def find_exec_in_path(exec_name):
    """
    :param str exec_name:
    :return: yields full paths
    :rtype: list[str]
    """
    if "PATH" not in os.environ:
        return
    for p in os.environ["PATH"].split(":"):
        pp = "%s/%s" % (p, exec_name)
        if os.path.exists(pp):
            yield pp


def get_pkg_config(pkg_config_args, *packages):
    """
    :param str|list[str] pkg_config_args: e.g. "--cflags"
    :param str packages: e.g. "python3"
    :rtype: list[str]|None
    """
    if not isinstance(pkg_config_args, (tuple, list)):
        pkg_config_args = [pkg_config_args]
    # Maybe we have multiple pkg-config, and maybe some of them finds it.
    for pp in find_exec_in_path("pkg-config"):
        try:
            out = check_output([pp] + list(pkg_config_args) + list(packages))
            return out.strip().decode("utf8").split()
        except CalledProcessError:
            pass
    return None


def get_python_linkopts():
    if LinkPython:
        link_opts = get_pkg_config("--libs", "python3" if Python3 else "python")
        assert link_opts is not None, "pkg-config failed"
        return link_opts
    else:
        return ["--weak-linking"]


def get_python_ccopts():
    flags = []
    if UsePyPy:
        # TODO use pkg-config or so
        flags += ["-I", "/usr/local/Cellar/pypy/1.9/include"]
    else:
        try:
            out = check_output(["python3-config" if Python3 else "python-config", "--cflags"])
            flags += out.strip().decode("utf8").split()
        except CalledProcessError:
            pkg_flags = get_pkg_config("--cflags", "python3" if Python3 else "python")
            if pkg_flags is not None:
                flags += pkg_flags
            else:
                # fallback to some defaults
                if Python3:
                    flags += [
                        "-I", "/usr/local/opt/python3/Frameworks/Python.framework/Versions/3.6/Headers",  # mac
                        "-I", "/usr/include/python3.6"
                    ]
                else:
                    flags += [
                        "-I", "/System/Library/Frameworks/Python.framework/Headers",  # mac
                        "-I", "/usr/include/python2.7",  # common linux/unix
                    ]
    pkg_flags = get_pkg_config("--cflags", *ffmpeg_packages)
    if pkg_flags is not None:
        flags += pkg_flags
    else:
        # fallback to some defaults
        flags += ["-I", "/usr/local/opt/ffmpeg/include"]
    return flags
