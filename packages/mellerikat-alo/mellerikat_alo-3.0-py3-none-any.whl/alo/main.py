import os
import sys
import argparse
import shutil

from alo.__version__ import __version__


def __run(args):
    from alo.alo import Alo
    from alo.model import settings, Git
    if args.name:
        settings.name = args.name
    if args.config:
        settings.config = args.config
    if args.system:
        settings.system = args.system
    if args.computing:
        settings.computing = args.computing
    settings.mode = None if args.mode == 'all' else args.mode
    if args.loop:
        settings.computing = 'daemon'
    if getattr(args, "git.url"):
        settings.git = Git(url=getattr(args, 'git.url'),
                           branch=getattr(args, 'git.branch') if getattr(args, 'git.branch') else 'main')
    if args.log_level:
        settings.log_level = args.log_level
    alo = Alo()
    alo.run()


def __template(args):
    # todo
    print("Coming soon.")


def __history(args):
    from alo.alo import Alo
    from alo.model import settings
    if args.config:
        settings.config = args.config
    alo = Alo()
    alo.history(type=args.mode, show_table=True, head=args.head, tail=args.tail)


def __register(args):
    import yaml

    def read_yaml(file_path):
        with open(file_path, 'r') as file:
            data = yaml.safe_load(file)
        return data

    def write_yaml(data, file_path):
        with open(file_path, 'w') as file:
            yaml.dump(data, file, default_flow_style=False, allow_unicode=True)

    def update_yaml(data, name=None, overview=None, detail=None):
        # Only update if the input is not empty
        if name and name.strip():  # name이 존재하고 공백이 아닌 경우에만 업데이트
            data['name'] = name
        if overview and overview.strip():  # overview가 존재하고 공백이 아닌 경우에만 업데이트
            data['overview'] = overview
        if detail:  # detail 리스트가 비어있지 않은 경우에만 업데이트
            data['detail'] = detail
        return data

    def copy_file_to_folder(src_file, dest_folder):
    # 복사하려는 파일이 존재하는지 확인합니다.
        if not os.path.isfile(src_file):
            print(f"{src_file} 파일을 찾을 수 없습니다.")
            return

        # 대상 폴더가 존재하지 않으면 생성합니다.
        if not os.path.exists(dest_folder):
            os.makedirs(dest_folder)

        # 파일명을 가져와 대상 폴더의 경로를 만듭니다.
        dest_file = os.path.join(dest_folder, os.path.basename(src_file))

        # 파일을 복사합니다.
        shutil.copy2(src_file, dest_file)
        print(f"{src_file} 파일이 {dest_file} 위치로 복사되었습니다.")

    from alo.solution_register import SolutionRegister
    src = os.getcwd()# os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'alo', 'example')
    settings = os.path.join(src, 'setting')
    solution_info = os.path.join(settings, 'solution_info.yaml')
    infra_config = os.path.join(settings, 'infra_config.yaml')

    data = read_yaml(solution_info)
    # Get user inputs for updating
    name = input("Enter the new name (leave empty to keep current): ")
    overview = input("Enter the new overview (leave empty to keep current): ")

    detail = []
    while True:
        add_detail = input("Do you want to add a detail? (yes/no): ").strip().lower()
        if add_detail == 'no':
            break
        content = input("Enter the content for the detail: ")
        title = input("Enter the title for the detail: ")
        detail.append({"content": content, "title": title})

    data = update_yaml(data, name, overview, detail)
    write_yaml(data, solution_info)

    current_settings_dir = os.path.join(os.getcwd(), 'setting')
    os.makedirs(current_settings_dir, exist_ok=True)
    # copy_file_to_folder(solution_info, current_settings_dir)
    # copy_file_to_folder(infra_config, current_settings_dir)

    solution_register = SolutionRegister(args.id, args.password)
    solution_register.register()


def __update(args):
    from alo.solution_register import SolutionRegister
    solution_register = SolutionRegister(args.id, args.password)
    solution_register.update()


def __delete(args):
    from alo.solution_register import SolutionRegister
    solution_register = SolutionRegister(args.id, args.password)
    solution_register.delete()


def __example(args):
    src = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'example', args.name)
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(os.getcwd(), item)
        if os.path.isdir(s):
            shutil.copytree(s, d)
        else:
            shutil.copy2(s, d)

    print(f"A {args.name} template file has been created in the current path.")
    print("Run alo")

def __docker(args):

    def print_ubuntu_package_instructions():

        instructions = """
        ### 우분투 패키지 설치 안내문 🌈

        안녕하세요! Dockerfile을 통해 우분투 패키지를 설치해보겠습니다. 아래의 단계를 따라 패키지를 추가해보세요:

        1. Dockerfile에서 `apt-get update` 명령을 포함하여 APT 패키지 목록을 업데이트하세요.

        2. `apt-get install` 명령을 사용하여 패키지를 설치하세요. `--no-install-recommends` 옵션을 사용하면 불필요한 의존성을 최소화할 수 있습니다.

        **예제**:
        우분투 패키지 `curl`을 설치하고 싶다면, Dockerfile의 해당 부분에 다음과 같이 추가하세요:

        ```dockerfile
        RUN apt-get update && \\
            apt-get install -y --no-install-recommends \\
            curl \\
            && rm -rf /var/lib/apt/lists/*

        추가된 curl 패키지는 Docker 컨테이너 내에서 사용 가능합니다.
        즐거운 ALO 생활 되세요 🐧
        """

        print(instructions)

    def print_cuda_instructions():

        instructions = """
        ### Docker container cuda와 cudnn 설정에 관한 안내문 🌈
        1. CUDA 버전 및 CuDNN 버전을 환경 변수로 정의합니다. Dockerfile 3번 라인과 4번 라인에 작성되어져 있는 변수 값을 정해줍니다.
        ARG ALO_CUDA_VER=11.2
        ARG ALO_CUDNN_VER=8.1

        2. 위 내용을 추가 하면 41번 라인에 의해서 cuda와 cudnn이 Container 안에 설치가 진행됩니다

        3. 위 내용을 추가 하면 53과 54번 라인에 의해서 cuda와 cudnn의 path가 Contianer 안에 설치가 진행됩니다

        4. 추가적으로 gpu에 대해서 수정하고 싶은 내용이 있다면 54번 라인 뒤에 작성하시면 됩니다

        5. 현재 구성되어진 cuda와 cudnn의 설정이 아닌 다른 내용이 필요 하다면 41번 부터 50번 라인, 53번과 54번 라인을 삭제 하고 직접 기술하시면 됩니다

        추가 참고 사항
        CUDA 및 CuDNN 설치는 CUDA 버전과 CuDNN의 호환성을 반드시 확인해야 합니다.
        NVIDIA 사이트에서 버전별 설치 가이드를 참고하면 더욱 정확한 설치가 가능합니다.
        주의사항: 호환성을 잘못 맞추면 예상치 못한 에러가 발생할 수 있습니다.
        도움이 되셨길 바랍니다! 필요에 따라 Dockerfile을 수정하여 나만의 Docker 이미지를 만들어보세요. 🚀 """

        print(instructions)

    dockerfile_src = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Dockerfiles', 'register', 'Dockerfile')
    dockerfile_dest = os.path.join(os.getcwd(), 'Dockerfile')
    print_ubuntu_package_instructions()
    print_cuda_instructions()
    if os.path.exists(dockerfile_src):
        shutil.copy2(dockerfile_src, dockerfile_dest)
        print(f"Dockerfile has been copied to the current path.")
    else:
        print("Error: Dockerfile not found.")

def main():
    if len(sys.argv) > 1:
        if sys.argv[-1] in ['-v', '--version']:
            print(__version__)
            return
        if sys.argv[1] in ['-h', '--help']:
            pass
        elif sys.argv[1] not in ['run', 'history', 'register', 'update', 'delete', 'template', 'example', 'docker']:  # v1 호환
            sys.argv.insert(1, 'run')
    else:
        sys.argv.insert(1, 'run')

    parser = argparse.ArgumentParser('alo', description='ALO(AI Learning Organizer)')
    parser.add_argument('-v', '--version', action='version', version=__version__)
    subparsers = parser.add_subparsers(dest='command')

    cmd_exec = subparsers.add_parser('run', description='Run alo')
    cmd_exec.add_argument('--name', type=str, help='name of solution')
    cmd_exec.add_argument('--mode', type=str, default='all', choices=['train', 'inference', 'all'], help='ALO mode: train, inference, all')
    cmd_exec.add_argument("--loop", dest='loop', action='store_true', help="On/off infinite loop: True, False")
    cmd_exec.add_argument("--computing", type=str, default="local", choices=['local', 'daemon'], help="training resource: local, ...")
    cmd_exec.add_argument('--config', type=str, help='path of experimental_plan.yaml')
    cmd_exec.add_argument('--system', type=str, help='path of solution_metadata.yaml')
    cmd_exec.add_argument('--git.url', type=str, help='url of git repository')
    cmd_exec.add_argument('--git.branch', type=str, help='branch name of git repository')
    cmd_exec.add_argument('--log_level', type=str, default="DEBUG", choices=['NOTSET', 'DEBUG', 'INFO', 'WARNING', 'ERROR'], help='log level')

    cmd_history = subparsers.add_parser('history', description='Run history')
    cmd_history.add_argument('--config', type=str, help='path of experimental_plan.yaml')
    cmd_history.add_argument('--mode', default=['train', 'inference'], choices=['train', 'inference'], nargs='+', help='train, inference')
    cmd_history.add_argument("--head", type=int, default=None, help="output the last part of history")
    cmd_history.add_argument("--tail", type=int, default=None, help="output the first part of history")

    cmd_template = subparsers.add_parser('template', description='Create titanic template')

    cmd_register = subparsers.add_parser('register', description='Create new solution')
    cmd_register.add_argument('--id', required=True, help='user id of AI conductor')
    cmd_register.add_argument('--password', required=True, help='user password of AI conductor')
    cmd_register.add_argument('--description', default=None, help='description')

    cmd_update = subparsers.add_parser('update', description='Update a solution')
    cmd_update.add_argument('--id', required=True, help='user id of AI conductor')
    cmd_update.add_argument('--password', required=True, help='user password of AI conductor')

    cmd_delete = subparsers.add_parser('delete', description='Delete a solution')
    cmd_delete.add_argument('--id', required=True, help='user id of AI conductor')
    cmd_delete.add_argument('--password', required=True, help='user password of AI conductor')

    cmd_example = subparsers.add_parser('example', description='Create ALO example')
    cmd_example.add_argument('--name', default='titanic', choices=['titanic'], help='Example of ALO')

    # Add docker command parser
    cmd_docker = subparsers.add_parser('docker', description='Create Dockerfile for ALO')

    args = parser.parse_args()

    commands = {'run': __run,
                'template': __template,
                'history': __history,
                'register': __register,
                'update': __update,
                'delete': __delete,
                'example': __example,
                'docker': __docker,
                }
    commands[args.command](args)
