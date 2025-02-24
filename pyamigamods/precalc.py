import cffi
from pyamigamods.loadlibs import loadlibs
import uuid

C, ffi = loadlibs()
ffi.cdef("""
        typedef struct  {
            int index;
            int length;
            char status[33];
        } subsong_t;

        typedef struct {
            char md5[33];
            subsong_t subsongs[256];
            int nb_subsongs;
            char format[256];
            char player[48];
            int channels;
            int size;
            char error_msg[1024];
            int exit_value;
        } module_t;
    """)
ffi.cdef("void cffi_precalc(char *path , module_t *module);")

class Subsong:
  def __init__(self, index,length,status):
    self.index = index
    self.length = length
    self.status = status
  def __iter__(self):
      yield self.index
      yield self.length
      yield self.status

class Module:
  def __init__(self, module=None):
    if module is not None:
        self.md5 = ffi.string(module.md5).decode("utf-8")
        self.nb_subsongs = module.nb_subsongs
        self.format = ffi.string(module.format).decode("utf-8")
        self.player = ffi.string(module.player).decode("utf-8")
        self.channels = module.channels
        self.size = module.size
        self.error_msg = ffi.string(module.error_msg).decode("utf-8")
        self.exit_value = module.exit_value
        self.subsongs = []
        for i in range(module.nb_subsongs):
            self.subsongs.append(Subsong(i,module.subsongs[i].length,ffi.string(module.subsongs[i].status).decode("utf-8")))
    else:
        self.subsongs = []
        md5_mock=uuid.uuid4().hex.upper()[0:32]
        self.md5 = md5_mock

def precalc_mod(module_path):
    #pymodule = Module(None)
    #return pymodule
    module=ffi.new("module_t *")
    module.exit_value=0
    module.error_msg=ffi.new("char[1024]", "".encode('utf-8'))
    module_path_encoded=""
    try:
        module_path_encoded = module_path.encode('utf-8')
    except UnicodeEncodeError as e:
        print(f"UnicodeEncodeError occurred: {e}")
        module_path_encoded=module_path.encode('utf-8', 'surrogateescape').decode('ISO-8859-1').encode('utf-8')
    C.cffi_precalc(module_path_encoded,module)
    pymodule=Module(module)
    return pymodule
