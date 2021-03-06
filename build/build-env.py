EnsureSConsVersion(1,2)

import os

import inspect
import platform

def get_cuda_paths():
  """Determines CUDA {bin,lib,include} paths
  
  returns (bin_path,lib_path,inc_path)
  """

  # determine defaults
  if os.name == 'nt':
    bin_path = 'C:/CUDA/bin'
    lib_path = 'C:/CUDA/lib'
    inc_path = 'C:/CUDA/include'
  elif os.name == 'posix':
    bin_path = '/usr/local/cuda/bin'
    lib_path = '/usr/local/cuda/lib'
    inc_path = '/usr/local/cuda/include'
  else:
    raise ValueError, 'Error: unknown OS.  Where is nvcc installed?'
   
  if platform.machine()[-2:] == '64':
    lib_path += '64'

  # override with environement variables
  if 'CUDA_BIN_PATH' in os.environ:
    bin_path = os.path.abspath(os.environ['CUDA_BIN_PATH'])
  if 'CUDA_LIB_PATH' in os.environ:
    lib_path = os.path.abspath(os.environ['CUDA_LIB_PATH'])
  if 'CUDA_INC_PATH' in os.environ:
    inc_path = os.path.abspath(os.environ['CUDA_INC_PATH'])

  return (bin_path,lib_path,inc_path)


def get_tbb_paths():
  """Determines TBB {lib,include} paths
  returns (lib_path,inc_path)
  """

  # determine defaults
  if os.name == 'nt':
    raise ValueError, 'Where is TBB installed?'
  else:
    lib_path = ''
    inc_path = ''

  return (lib_path,inc_path)


def getTools():
  result = []
  if os.name == 'nt':
    result = ['default', 'msvc']
  elif os.name == 'posix':
    result = ['default', 'gcc']
  else:
    result = ['default']
  return result;


OldEnvironment = Environment;


# this dictionary maps the name of a compiler program to a dictionary mapping the name of
# a compiler switch of interest to the specific switch implementing the feature
gCompilerOptions = {
    'gcc' : {'warn_all' : '-Wall', 'warn_errors' : '-Werror', 'optimization' : '-O2', 'debug' : '-g',  'exception_handling' : '',      'omp' : '-fopenmp'},
    'g++' : {'warn_all' : '-Wall', 'warn_errors' : '-Werror', 'optimization' : '-O2', 'debug' : '-g',  'exception_handling' : '',      'omp' : '-fopenmp'},
    'cl'  : {'warn_all' : '/Wall', 'warn_errors' : '/WX',     'optimization' : '/Ox', 'debug' : ['/Zi', '-D_DEBUG', '/MTd'], 'exception_handling' : '/EHsc', 'omp' : '/openmp'}
  }


# this dictionary maps the name of a linker program to a dictionary mapping the name of
# a linker switch of interest to the specific switch implementing the feature
gLinkerOptions = {
    'gcc'   : {'debug' : ''},
    'g++'   : {'debug' : ''},
    'link'  : {'debug' : '/debug' }
  }


def getCFLAGS(mode, host_backend, backend, warn, warnings_as_errors, CC):
  result = []
  if mode == 'release':
    # turn on optimization
    result.append(gCompilerOptions[CC]['optimization'])
  elif mode == 'debug':
    # turn on debug mode
    result.append(gCompilerOptions[CC]['debug'])
    result.append('-DTHRUST_DEBUG')
  # force 32b code on darwin
  if platform.platform()[:6] == 'Darwin':
    result.append('-m32')

  # generate omp code
  if host_backend == 'omp' or backend == 'omp':
    result.append(gCompilerOptions[CC]['omp'])

  if warn:
    # turn on all warnings
    result.append(gCompilerOptions[CC]['warn_all'])

  if warnings_as_errors:
    # treat warnings as errors
    result.append(gCompilerOptions[CC]['warn_errors'])

  # avoid problems specific to windows
  if CC == 'cl':
    # avoid min/max problems due to windows.h
    result.append('/DNOMINMAX')
    # suppress warnings due to "decorated name length exceeded"
    result.append('/wd4503')

  return result


def getCXXFLAGS(mode, host_backend, backend, warn, warnings_as_errors, CXX):
  result = []
  if mode == 'release':
    # turn on optimization
    result.append(gCompilerOptions[CXX]['optimization'])
  elif mode == 'debug':
    # turn on debug mode
    result.append(gCompilerOptions[CXX]['debug'])
  # enable exception handling
  result.append(gCompilerOptions[CXX]['exception_handling'])
  # force 32b code on darwin
  if platform.platform()[:6] == 'Darwin':
    result.append('-m32')

  # generate omp code
  if host_backend == 'omp' or backend == 'omp':
    result.append(gCompilerOptions[CXX]['omp'])

  if warn:
    # turn on all warnings
    result.append(gCompilerOptions[CXX]['warn_all'])

  if warnings_as_errors:
    # treat warnings as errors
    result.append(gCompilerOptions[CXX]['warn_errors'])

  return result


def getNVCCFLAGS(mode, host_backend, backend, arch):
  result = ['-arch=' + arch]
  if mode == 'debug':
    # turn on debug mode
    # XXX make this work when we've debugged nvcc -G
    #result.append('-G')
    pass
  if backend != 'cuda':
    result.append("--x=c++")
  return result


def getLINKFLAGS(mode, host_backend, backend, LINK):
  result = []
  if mode == 'debug':
    # turn on debug mode
    result.append(gLinkerOptions[LINK]['debug'])
  # force 32b code on darwin
  if platform.platform()[:6] == 'Darwin':
    result.append('-m32')

  # XXX make this portable
  if backend == 'ocelot':
    result.append(os.popen('OcelotConfig -l').read().split())

  return result


def Environment():
  # allow the user discretion to choose the MSVC version
  vars = Variables()
  if os.name == 'nt':
    vars.Add(EnumVariable('MSVC_VERSION', 'MS Visual C++ version', None, allowed_values=('8.0', '9.0', '10.0')))

  # add a variable to handle the device backend
  backend_variable = EnumVariable('backend', 'The parallel device backend to target', 'cuda',
                                  allowed_values = ('cuda', 'omp', 'ocelot', 'tbb'))
  vars.Add(backend_variable)

  # add a variable to handle the host backend
  host_backend_variable = EnumVariable('host_backend', 'The host backend to target', 'cpp',
                                       allowed_values = ('cpp', 'omp', 'tbb'))
  vars.Add(host_backend_variable)

  # add a variable to handle RELEASE/DEBUG mode
  vars.Add(EnumVariable('mode', 'Release versus debug mode', 'release',
                        allowed_values = ('release', 'debug')))

  # add a variable to handle compute capability
  vars.Add(EnumVariable('arch', 'Compute capability code generation', 'sm_10',
                        allowed_values = ('sm_10', 'sm_11', 'sm_12', 'sm_13', 'sm_20', 'sm_21')))

  # add a variable to handle warnings
  if os.name == 'posix':
    vars.Add(BoolVariable('Wall', 'Enable all compilation warnings', 1))
  else:
    vars.Add(BoolVariable('Wall', 'Enable all compilation warnings', 0))

  # add a variable to treat warnings as errors
  vars.Add(BoolVariable('Werror', 'Treat warnings as errors', 0))

  # add a variable to filter source files by a regex
  vars.Add('tests', help='Filter test files using a regex')

  # create an Environment
  env = OldEnvironment(tools = getTools(), variables = vars)

  # get the absolute path to the directory containing
  # this source file
  thisFile = inspect.getabsfile(Environment)
  thisDir = os.path.dirname(thisFile)

  # enable nvcc
  env.Tool('nvcc', toolpath = [os.path.join(thisDir)])

  # get the preprocessor define to use for the device backend
  backend_define = { 'cuda' : 'THRUST_DEVICE_SYSTEM_CUDA', 'omp' : 'THRUST_DEVICE_SYSTEM_OMP', 'ocelot' : 'THRUST_DEVICE_SYSTEM_CUDA', 'tbb' : 'THRUST_DEVICE_SYSTEM_TBB' }[env['backend']] 
  env.Append(CFLAGS   = ['-DTHRUST_DEVICE_SYSTEM=%s' % backend_define])
  env.Append(CXXFLAGS = ['-DTHRUST_DEVICE_SYSTEM=%s' % backend_define])

  # get the preprocessor define to use for the host system
  host_backend_define = { 'cpp' : 'THRUST_HOST_SYSTEM_CPP', 'omp' : 'THRUST_HOST_SYSTEM_OMP', 'tbb' : 'THRUST_HOST_SYSTEM_TBB' }[env['host_backend']] 
  env.Append(CFLAGS   = ['-DTHRUST_HOST_SYSTEM=%s' % host_backend_define])
  env.Append(CXXFLAGS = ['-DTHRUST_HOST_SYSTEM=%s' % host_backend_define])

  # get C compiler switches
  env.Append(CFLAGS = getCFLAGS(env['mode'], env['host_backend'], env['backend'], env['Wall'], env['Werror'], env.subst('$CC')))

  # get CXX compiler switches
  env.Append(CXXFLAGS = getCXXFLAGS(env['mode'], env['host_backend'], env['backend'], env['Wall'], env['Werror'], env.subst('$CXX')))

  # get NVCC compiler switches
  env.Append(NVCCFLAGS = getNVCCFLAGS(env['mode'], env['host_backend'], env['backend'], env['arch']))

  # get linker switches
  env.Append(LINKFLAGS = getLINKFLAGS(env['mode'], env['host_backend'], env['backend'], env.subst('$LINK')))
   
  # get CUDA paths
  (cuda_exe_path,cuda_lib_path,cuda_inc_path) = get_cuda_paths()
  env.Append(LIBPATH = [cuda_lib_path])
  env.Append(CPPPATH = [cuda_inc_path])

  # get TBB paths
  (tbb_lib_path,tbb_inc_path) = get_tbb_paths()
  env.Append(LIBPATH = [tbb_lib_path])
  env.Append(CPPPATH = [tbb_inc_path])

  # link against the standard library
  # we don't have to do this on Windows
  if os.name == 'posix':
    env.Append(LIBS = ['stdc++'])

  # link against backend-specific runtimes
  # XXX we shouldn't have to link against cudart unless we're using the
  #     cuda runtime, but cudafe inserts some dependencies when compiling .cu files
  # XXX ideally this gets handled in nvcc.py if possible
  env.Append(LIBS = ['cudart'])

  if env['backend'] == 'ocelot':
    if os.name == 'posix':
      env.Append(LIBPATH = ['/usr/local/lib'])
    else:
      raise ValueError, "Unknown OS.  What is the Ocelot library path?"

  if env['host_backend'] == 'omp' or env['backend'] == 'omp':
    if os.name == 'posix':
      env.Append(LIBS = ['gomp'])
    elif os.name == 'nt':
      env.Append(LIBS = ['VCOMP'])
    else:
      raise ValueError, "Unknown OS.  What is the name of the OpenMP library?"

  if env['host_backend'] == 'tbb' or env['backend'] == 'tbb':
    env.Append(LIBS = ['tbb'])

  # set thrust include path
  # this needs to come before the CUDA include path appended above,
  # which may include a different version of thrust
  env.Prepend(CPPPATH = os.path.dirname(thisDir))

  # import the LD_LIBRARY_PATH so we can run commands which depend
  # on shared libraries
  # XXX we should probably just copy the entire environment
  if os.name == 'posix':
    if env['PLATFORM'] == "darwin":
      env['ENV']['DYLD_LIBRARY_PATH'] = os.environ['DYLD_LIBRARY_PATH']
    else:
      env['ENV']['LD_LIBRARY_PATH'] = os.environ['LD_LIBRARY_PATH']

  # generate help text
  Help(vars.GenerateHelpText(env))

  return env

