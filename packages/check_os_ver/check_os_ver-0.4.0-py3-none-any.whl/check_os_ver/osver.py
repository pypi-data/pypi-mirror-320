import subprocess
import sys

# OS를 확인하는 함수(macOS, Lunux만 구현)
def get_os_version() -> str:
    if sys.platform == "darwin":
        return get_os_version_of_mac()
    elif sys.platform.startswith("linux"):
        return get_os_version_of_linux()
    else:
        return "Unsupported platform"

# OS가 Linux인 경우 처리하는 함수
def get_os_version_of_linux() -> str:
    with open('/etc/os-release', 'r') as file:
        for line in file:
            if line.startswith('PRETTY_NAME'):
                return line.split('=')[1].replace('\n','').strip("\"")
    return None

# OS가 mac인 경우 처리하는 함수
def get_os_version_of_mac() -> str:
    # 파이썬에서 터미널 명령어를 실행하고 결과를 원하는 형태로 변경하는 함수
    def get_macro_reply(command):
        result = subprocess.run([command], shell=True, capture_output=True, text=True).stdout
        lines = result.splitlines()
        if lines:
             return lines[0].split(":")[1].strip()
        return None

    system_filter_command = "system_profiler SPSoftwareDataType | grep 'System Version'"
    kernel_filter_command = "system_profiler SPSoftwareDataType | grep 'Kernel Version'"

    system_version = get_macro_reply(system_filter_command)
    kernel_version = get_macro_reply(kernel_filter_command)

    return system_version + ', ' + kernel_version
