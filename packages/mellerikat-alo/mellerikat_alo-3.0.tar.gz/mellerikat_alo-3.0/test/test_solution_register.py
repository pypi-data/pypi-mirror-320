import unittest
from unittest.mock import Mock, patch, MagicMock
import boto3
import docker
from botocore.exceptions import ClientError
from alo.solution_register import SolutionRegister  # 원본 코드 import

import unittest
from unittest.mock import Mock, patch, MagicMock
import boto3
import docker
from botocore.exceptions import ClientError

class TestSolutionRegisterCleanup(unittest.TestCase):
    def setUp(self):
        """테스트 설정"""
        # SolutionRegister 클래스의 인스턴스 생성
        self.solution_register = SolutionRegister("test_user", "test_pw")
        self.solution_register.bucket_name = "test-bucket"
        self.solution_register.__name = "test-solution"
        self.solution_register.__version_num = 1
        self.solution_register.ecr_repo = "test-repo"
        self.solution_register.ecr_full_url = "test.ecr.aws/test-repo"
        self.solution_register.pipeline = "train"

    @patch('boto3.client')
    def test_cleanup_s3_data(self, mock_boto3_client):
        """S3 데이터 정리 테스트"""
        # Mock S3 클라이언트 설정
        mock_s3 = Mock()
        mock_boto3_client.return_value = mock_s3

        # S3 객체 리스트 응답 설정
        mock_s3.list_objects_v2.return_value = {
            'Contents': [
                {'Key': 'test/file1.txt'},
                {'Key': 'test/file2.txt'}
            ]
        }

        # 정리 메소드 실행
        self.solution_register._cleanup_s3_data()

        # S3 클라이언트 호출 확인
        mock_s3.list_objects_v2.assert_called_once()
        mock_s3.delete_objects.assert_called_once()

        # 빈 버킷 케이스 테스트
        mock_s3.list_objects_v2.return_value = {}
        self.solution_register._cleanup_s3_data()
        self.assertEqual(mock_s3.delete_objects.call_count, 1)  # 추가 호출 없음

    @patch('shutil.rmtree')
    @patch('boto3.client')
    def test_cleanup_artifacts(self, mock_boto3_client, mock_rmtree):
        """아티팩트 정리 테스트"""
        # Mock S3 클라이언트 설정
        mock_s3 = Mock()
        mock_boto3_client.return_value = mock_s3

        # S3 객체 리스트 응답 설정
        mock_s3.list_objects_v2.return_value = {
            'Contents': [
                {'Key': 'artifacts/file1.txt'},
                {'Key': 'artifacts/file2.txt'}
            ]
        }

        # 정리 메소드 실행
        self.solution_register._cleanup_artifacts()

        # 검증
        mock_s3.list_objects_v2.assert_called_once()
        mock_s3.delete_objects.assert_called_once()
        mock_rmtree.assert_called_once()

    @patch('docker.from_env')
    @patch('boto3.client')
    def test_cleanup_docker_resources(self, mock_boto3_client, mock_docker):
        """Docker 리소스 정리 테스트"""
        # Mock ECR 클라이언트 설정
        mock_ecr = Mock()
        mock_boto3_client.return_value = mock_ecr

        # Mock Docker 클라이언트 설정
        mock_docker_client = Mock()
        mock_docker.return_value = mock_docker_client

        # Docker 빌드 방식 설정
        self.solution_register.infra_config = {'BUILD_METHOD': 'docker'}

        # 정리 메소드 실행
        self.solution_register._cleanup_docker_resources()

        # ECR 이미지 삭제 확인
        mock_ecr.batch_delete_image.assert_called_once()

        # Docker 이미지 삭제 확인
        mock_docker_client.images.remove.assert_called_once()

    @patch('subprocess.run')
    @patch('boto3.client')
    def test_cleanup_docker_resources_buildah(self, mock_boto3_client, mock_subprocess):
        """Buildah 리소스 정리 테스트"""
        # Mock ECR 클라이언트 설정
        mock_ecr = Mock()
        mock_boto3_client.return_value = mock_ecr

        # Buildah 빌드 방식 설정
        self.solution_register.infra_config = {'BUILD_METHOD': 'buildah'}

        # 정리 메소드 실행
        self.solution_register._cleanup_docker_resources()

        # ECR 이미지 삭제 확인
        mock_ecr.batch_delete_image.assert_called_once()

        # Buildah 명령어 실행 확인
        mock_subprocess.assert_called_once()

    @patch.object(SolutionRegister, '_cleanup_docker_resources')
    @patch.object(SolutionRegister, '_cleanup_artifacts')
    @patch.object(SolutionRegister, '_cleanup_s3_data')
    def test_cleanup_all_resources(self, mock_s3, mock_artifacts, mock_docker):
        """전체 리소스 정리 테스트"""
        # 정상 케이스
        self.solution_register.cleanup_all_resources()
        mock_docker.assert_called_once()
        mock_artifacts.assert_called_once()
        mock_s3.assert_called_once()

        # 일부 실패 케이스
        mock_docker.side_effect = Exception("Docker cleanup failed")
        mock_artifacts.side_effect = Exception("Artifacts cleanup failed")

        with self.assertRaises(Exception) as context:
            self.solution_register.cleanup_all_resources()

        self.assertIn("Failed to cleanup one or more resources", str(context.exception))

    def test_run_pipeline_with_cleanup(self):
        """파이프라인 실행 중 실패 시 정리 테스트"""
        # Mock 설정
        self.solution_register.s3_upload_data = Mock()
        self.solution_register.s3_upload_artifacts = Mock()
        self.solution_register.make_docker = Mock()
        self.solution_register.docker_push = Mock()
        self.solution_register._set_container_uri = Mock()
        self.solution_register.cleanup_all_resources = Mock()

        # 아티팩트 업로드 실패 시나리오
        self.solution_register.s3_upload_artifacts.side_effect = Exception("Artifact upload failed")

        with self.assertRaises(Exception):
            self.solution_register.run_pipeline("train")

        # S3 데이터 정리만 호출되었는지 확인
        self.solution_register._cleanup_s3_data.assert_called_once()
        self.solution_register.cleanup_all_resources.assert_not_called()

        # Docker 작업 실패 시나리오
        self.solution_register.s3_upload_artifacts.side_effect = None
        self.solution_register.docker_push.side_effect = Exception("Docker push failed")

        with self.assertRaises(Exception):
            self.solution_register.run_pipeline("train")

        # 모든 리소스 정리가 호출되었는지 확인
        self.solution_register.cleanup_all_resources.assert_called_once()

if __name__ == '__main__':
    unittest.main()