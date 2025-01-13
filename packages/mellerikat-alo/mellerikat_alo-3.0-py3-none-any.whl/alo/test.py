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