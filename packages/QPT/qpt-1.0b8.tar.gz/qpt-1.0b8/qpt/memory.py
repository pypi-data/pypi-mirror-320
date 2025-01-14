# Author: Acer Zhang
# Datetime:2021/7/3 
# Copyright belongs to the author.
# Please indicate the source for reprinting.

import os
import sys
import platform
from distutils.sysconfig import get_python_lib

from qpt.kernel.qlog import Logging


def init_wrapper(var=False):
    """
    缓存器，若为首次运行则会初始化，后续无特殊情况
    :param var: 是否包含参数
    """

    def i_wrapper(func):
        if not var:
            @property
            def render(self):
                if func.__name__ in self.memory:
                    out = self.memory[func.__name__]
                else:
                    out = func(self)
                    self.memory[func.__name__] = out
                return out
        else:
            def render(self, *args, **kwargs):
                if func.__name__ in self.memory:
                    out = self.memory[func.__name__]
                else:
                    out = func(self, *args, **kwargs)
                    self.memory[func.__name__] = out
                return out
        return render

    return i_wrapper


class QPTMemory:
    def __init__(self):
        self.memory = dict()

    def set_mem(self, name, variable):
        self.memory[name] = variable
        return variable

    def free_mem(self, name):
        self.memory.pop(name)

    @init_wrapper()
    def platform_bit(self):
        arc = platform.machine()
        Logging.debug(f"操作系统位数：{arc}")
        return arc

    @init_wrapper()
    def platform_os(self):
        p_os = platform.system()
        Logging.debug(f"操作系统类型：{p_os}")
        return p_os

    @init_wrapper()
    def site_packages_path(self):
        site_package_path = os.path.abspath(get_python_lib())
        return site_package_path

    @init_wrapper()
    def pip_tool(self):
        from qpt.kernel.qinterpreter import PipTools
        pip_tools = PipTools()
        return pip_tools

    @init_wrapper()
    def pip_tool_in_this_env(self):
        from qpt.kernel.qinterpreter import PipTools
        pip_tools = PipTools(env_path=sys.executable)
        return pip_tools

    @init_wrapper()
    def get_win32con(self):
        import win32con
        return win32con

    @init_wrapper()
    def get_win32api(self):
        import win32api
        return win32api

    @init_wrapper()
    def get_qpt_sdk_list(self):
        from QPT_SDK.loc import QPT_SDK_PATH
        path_list = os.listdir(QPT_SDK_PATH)
        sdk_list = [path.lower() for path in path_list if os.path.isdir(path)]
        return sdk_list

    @init_wrapper(var=True)
    def get_env_vars(self, work_dir="."):
        return get_env_vars(work_dir)

    @init_wrapper()
    def get_down_packages_relative_path(self):
        return "opt/packages"

    @init_wrapper()
    def action_flag(self):
        flag = os.environ.get("QPT_Action", default=False)
        return flag


QPT_MEMORY = QPTMemory()


def check_bit():
    arc = QPT_MEMORY.platform_bit
    assert "64" in arc, "当前QPT不支持32位操作系统"


def check_os():
    p_os = QPT_MEMORY.platform_os
    assert "Windows" in p_os, "当前QPT只支持Windows系统"


def check_pip():
    from pip import __version__

    _ver = __version__.split(".")
    _ver.reverse()

    _ver_num = 0
    for _v_id, _v in enumerate(_ver):
        _num = 10 ** (_v_id + 1) * int(_v)
        _ver_num += _num

    if _ver_num < 2211:
        raise EnvironmentError(f"当前Python环境下pip版本为{__version__}，QPT需要您使用版本号高于22.1.1的pip模块！\n"
                               f"请在当前环境下使用python -m install -U pip，若您不了解如何管理Python环境，"
                               f"无法实现pip的升级操作，请自行搜索相应解决方案或补充Python开发基础。")


IGNORE_ENV_FIELD = ["conda", "Conda", "Python", "python"]


def get_env_vars(work_dir="."):
    # ToDo 确定是否还要走这步
    """
    获取当前待设置的环境变量字典
    :param work_dir:
    :return: dict
    """
    env_vars = dict()
    # Set PATH ENV
    path_env = os.environ.get("PATH").split(";")
    pre_add_env = os.path.abspath("./Python/Lib/site-packages") + ";" + \
                  os.path.abspath("./Python/Lib") + ";" + \
                  os.path.abspath("./Python/Lib/ext") + ";" + \
                  os.path.abspath("./Python") + ";" + \
                  os.path.abspath("./Python/Scripts") + ";"

    for pe in path_env:
        if pe:
            add_flag = True
            for ief in IGNORE_ENV_FIELD:
                if ief in pe:
                    add_flag = False
                    break
            if add_flag:
                pre_add_env += pe + ";"
    env_vars["PATH"] = pre_add_env + \
                       "%SYSTEMROOT%/System32/WindowsPowerShell/v1.0;" + \
                       "C:/Windows/System32/WindowsPowerShell/v1.0;" + \
                       "%ProgramFiles%/WindowsPowerShell/Modules;" + \
                       "%SystemRoot%/system32/WindowsPowerShell/v1.0/Modules;" + \
                       f"{os.path.join(os.path.abspath(work_dir), 'opt/CUDA')};"

    # Set PYTHON PATH ENV
    env_vars["PYTHONPATH"] = os.path.abspath("./Python/Lib/site-packages") + ";" + \
                             work_dir + ";" + \
                             os.path.abspath("./Python")
    os_env = os.environ.copy()
    os_env.update(env_vars)

    if QPT_MODE and QPT_MODE.lower() == "debugging":
        Logging.debug(msg="Python所识别到的环境变量如下：\n" +
                          "".join([_ek + ":" + _e_v + " \n" for _ek, _ev in env_vars.items()
                                   for _e_v in _ev.split(";")]))

    return os_env


PYTHON_IGNORE_DIRS = [".idea", ".git", ".github", "venv"]

# 被忽略的Python包
IGNORE_PACKAGES = ["virtualenv", "pip", "setuptools", "cpython"]

# QPT运行状态 Run/Debug 在运行后更改为Running/Debug
QPT_MODE = os.getenv("QPT_MODE")

# QPT检测到的运行状态 Run/本地Run - 目的给予开发者警告，避免软件包膨胀
QPT_RUN_MODE = None


class CheckRun:
    @staticmethod
    def make_run_file(configs_path):
        with open(os.path.join(configs_path, "run_act.lock"), "w") as f:
            f.write("Run Done")

    @staticmethod
    def check_run_file(configs_path):
        global QPT_RUN_MODE
        if QPT_RUN_MODE is None:
            QPT_RUN_MODE = os.path.exists(os.path.join(configs_path, "run_act.lock"))
        return QPT_RUN_MODE


def check_all():
    # 检查系统
    check_os()
    # 检查arc
    check_bit()
    # 检查pip版本
    check_pip()


check_all()
