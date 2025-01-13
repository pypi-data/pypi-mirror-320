import json
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
import os
import inspect
import sys

class UpdateAPI:
    def __init__(self):
        self.router = APIRouter(prefix="/api/v1")
        self.setup_routes()

        # 현재 실행 중인 메인 스크립트의 경로 찾기
        main_module = sys.modules['__main__']
        # if hasattr(main_module, '__file__'):
        #     main_path = os.path.dirname(os.path.abspath(main_module.__file__))
        # else:
            # 실행 중인 스크립트를 찾을 수 없는 경우 현재 작업 디렉토리 사용
        main_path = os.getcwd()

        # config 디렉토리 경로 설정
        self.language_file = os.path.join(main_path, "config", "language_setting.json")
        self.prompt_path = os.path.join(main_path, "prompts")
        self.supported_languages = ["korean", "english", "japanese"]

        # config 디렉토리가 없으면 생성
        os.makedirs(os.path.dirname(self.language_file), exist_ok=True)

        # 기본 언어 설정 파일이 없으면 생성
        if not os.path.exists(self.language_file):
            self.save_language_setting("korean")

    class UpdateRequest(BaseModel):
        language: str

    class UpdateResponse(BaseModel):
        status: str
        message: str
        language: str

    # 새로운 Request 모델 추가
    class FileUpdateRequest(BaseModel):
        filename: str
        content: str

    # 새로운 Response 모델 추가
    class FileUpdateResponse(BaseModel):
        status: str
        message: str
        filename: str

    def save_language_setting(self, language: str):
        """언어 설정을 파일로 저장"""
        try:
            with open(self.language_file, 'w', encoding='utf-8') as f:
                json.dump({"current_language": language}, f)
        except Exception as e:
            raise Exception(f"Failed to save language setting to {self.language_file}: {str(e)}")

    def setup_routes(self):
        @self.router.post("/update_rag", response_model=self.UpdateResponse)
        async def comming_soon(request: self.UpdateRequest):
            try:
                if request.language not in self.supported_languages:
                    raise ValueError(f"Unsupported language: {request.language}. Supported languages are: {self.supported_languages}")

                self.save_language_setting(request.language)

                return {
                    "status": "success",
                    "message": f"Language updated to {request.language}",
                    "language": request.language
                }
            except ValueError as e:
                raise HTTPException(
                    status_code=400,
                    detail=str(e)
                )
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Language update failed: {str(e)}"
                )

        # 새로운 파일 업데이트 라우트 추가
        @self.router.post("/update_prompt", response_model=self.FileUpdateResponse)
        async def update_file(
            filename: str = Query(..., description="파일 이름"),
            contents: str = Query(..., description="파일 내용")
        ):
            try:
                file_path = os.path.join(self.prompt_path, filename)

                # 파일이 config 디렉토리 내에 있는지 확인
                if not os.path.abspath(file_path).startswith(os.path.abspath(self.prompt_path)):
                    raise ValueError("File must be located in the config directory")

                # 문자열을 JSON 객체로 변환하고 저장
                try:
                    json_content = json.loads(contents)
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(json_content, f, ensure_ascii=False, indent=4)
                except json.JSONDecodeError:
                    raise ValueError("Invalid JSON format")

                return {
                    "status": "success",
                }
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"File update failed: {str(e)}"
                )


    def get_router(self):
        """라우터 반환 메서드 추가"""
        return self.router