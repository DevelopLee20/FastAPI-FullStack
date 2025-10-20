"""
.env File Sync Service
DB의 환경변수를 .env 파일로 백업/동기화
"""
import os
from datetime import datetime
from typing import Dict


class EnvSyncService:
    """
    환경변수 .env 파일 동기화 서비스

    서비스 종료 시 DB의 최신 환경변수를 .env 파일로 백업
    """

    @staticmethod
    def export_to_env_file(
        env_dict: Dict[str, str],
        output_path: str = ".env",
        backup: bool = True
    ) -> bool:
        """
        환경변수 딕셔너리를 .env 파일로 내보내기

        Args:
            env_dict: 환경변수 딕셔너리
            output_path: 출력 파일 경로 (기본: .env)
            backup: 기존 파일 백업 여부

        Returns:
            성공 여부
        """
        try:
            # 기존 파일 백업
            if backup and os.path.exists(output_path):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = f"{output_path}.backup.{timestamp}"
                os.rename(output_path, backup_path)
                # TODO: LOG 추가 - print(f"Backup created: {backup_path}")

            # .env 파일 작성
            with open(output_path, "w", encoding="utf-8") as f:
                # 헤더 작성
                f.write("# Environment Variables\n")
                f.write(f"# Exported from Database at {datetime.now().isoformat()}\n")
                f.write("# DO NOT EDIT MANUALLY - Changes will be overwritten\n\n")

                # 환경변수 작성 (알파벳 순 정렬)
                for key in sorted(env_dict.keys()):
                    value = env_dict[key]
                    # 특수문자나 공백이 있는 경우 따옴표로 감싸기
                    if " " in value or any(c in value for c in ['$', '#', '"', "'"]):
                        value = f'"{value}"'
                    f.write(f"{key}={value}\n")

            # TODO: LOG 추가 - print(f"Environment variables exported to {output_path} ({len(env_dict)} variables)")
            return True

        except Exception as e:
            # TODO: LOG 추가 - print(f"Failed to export environment variables to {output_path}: {e}")
            return False

    @staticmethod
    def load_from_env_file(file_path: str = ".env") -> Dict[str, str]:
        """
        .env 파일에서 환경변수 로드

        Args:
            file_path: .env 파일 경로

        Returns:
            환경변수 딕셔너리
        """
        from dotenv import dotenv_values

        if not os.path.exists(file_path):
            # TODO: LOG 추가 - print(f"Warning: {file_path} not found")
            return {}

        try:
            env_dict = dotenv_values(file_path)
            # None 값 제거
            env_dict = {k: v for k, v in env_dict.items() if v is not None}
            # TODO: LOG 추가 - print(f"Loaded {len(env_dict)} environment variables from {file_path}")
            return env_dict

        except Exception as e:
            # TODO: LOG 추가 - print(f"Failed to load environment variables from {file_path}: {e}")
            return {}

    @staticmethod
    def merge_env_files(
        source_path: str,
        target_path: str,
        overwrite: bool = False
    ) -> bool:
        """
        두 .env 파일 병합

        Args:
            source_path: 소스 .env 파일
            target_path: 대상 .env 파일
            overwrite: 중복 키 덮어쓰기 여부

        Returns:
            성공 여부
        """
        try:
            source_dict = EnvSyncService.load_from_env_file(source_path)
            target_dict = EnvSyncService.load_from_env_file(target_path)

            # 병합
            if overwrite:
                # 소스가 대상을 덮어씀
                merged = {**target_dict, **source_dict}
            else:
                # 대상 우선 (중복 시 대상 값 유지)
                merged = {**source_dict, **target_dict}

            # 병합 결과 저장
            return EnvSyncService.export_to_env_file(
                merged,
                output_path=target_path,
                backup=True
            )

        except Exception as e:
            # TODO: LOG 추가 - print(f"Failed to merge env files: {e}")
            return False

    @staticmethod
    def validate_env_file(file_path: str = ".env") -> tuple[bool, list[str]]:
        """
        .env 파일 유효성 검증

        Args:
            file_path: .env 파일 경로

        Returns:
            (유효성 여부, 오류 메시지 리스트)
        """
        errors = []

        if not os.path.exists(file_path):
            return False, [f"File not found: {file_path}"]

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()

                    # 빈 줄이나 주석 무시
                    if not line or line.startswith("#"):
                        continue

                    # KEY=VALUE 형식 검증
                    if "=" not in line:
                        errors.append(f"Line {line_num}: Missing '=' separator")
                        continue

                    key, _ = line.split("=", 1)
                    key = key.strip()

                    # 키 검증
                    if not key:
                        errors.append(f"Line {line_num}: Empty key")
                    elif not key.replace("_", "").isalnum():
                        errors.append(
                            f"Line {line_num}: Invalid key '{key}' "
                            "(only alphanumeric and underscore allowed)"
                        )

            return len(errors) == 0, errors

        except Exception as e:
            return False, [f"Failed to read file: {e}"]

    @staticmethod
    def get_backup_files(base_path: str = ".env") -> list[str]:
        """
        백업 파일 목록 조회

        Args:
            base_path: 기본 .env 파일 경로

        Returns:
            백업 파일 경로 리스트 (최신순)
        """
        import glob

        pattern = f"{base_path}.backup.*"
        backup_files = glob.glob(pattern)

        # 수정 시간 기준 최신순 정렬
        backup_files.sort(key=os.path.getmtime, reverse=True)

        return backup_files

    @staticmethod
    def restore_from_backup(backup_path: str, target_path: str = ".env") -> bool:
        """
        백업 파일로부터 복원

        Args:
            backup_path: 백업 파일 경로
            target_path: 복원할 파일 경로

        Returns:
            성공 여부
        """
        try:
            if not os.path.exists(backup_path):
                # TODO: LOG 추가 - print(f"Backup file not found: {backup_path}")
                return False

            # 현재 파일 백업 (이중 백업)
            if os.path.exists(target_path):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                safety_backup = f"{target_path}.before_restore.{timestamp}"
                os.rename(target_path, safety_backup)
                # TODO: LOG 추가 - print(f"Safety backup created: {safety_backup}")

            # 백업에서 복원
            import shutil
            shutil.copy2(backup_path, target_path)
            # TODO: LOG 추가 - print(f"Restored from {backup_path} to {target_path}")
            return True

        except Exception as e:
            # TODO: LOG 추가 - print(f"Failed to restore from backup: {e}")
            return False
