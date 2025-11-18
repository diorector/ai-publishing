# 체크포인트 관리 유틸리티
# 작성일: 2025-11-18
# 목적: 편집 중간 진행 상황 저장 및 복구

import json
import pickle
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime


class CheckpointManager:
    """편집 체크포인트 관리 (중단 후 재개 기능)"""

    def __init__(self, checkpoint_dir: str = ".checkpoints"):
        """초기화"""
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(exist_ok=True)

    def save_checkpoint(
        self,
        doc_id: str,
        stage: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """체크포인트 저장"""
        checkpoint_data = {
            'doc_id': doc_id,
            'stage': stage,
            'content': content,
            'metadata': metadata or {},
            'timestamp': datetime.now().isoformat(),
        }

        checkpoint_file = self.checkpoint_dir / f"{doc_id}_{stage}.json"

        with open(checkpoint_file, 'w', encoding='utf-8') as f:
            json.dump(checkpoint_data, f, ensure_ascii=False, indent=2)

        return str(checkpoint_file)

    def load_checkpoint(self, doc_id: str, stage: str) -> Optional[Dict[str, Any]]:
        """체크포인트 로드"""
        checkpoint_file = self.checkpoint_dir / f"{doc_id}_{stage}.json"

        if not checkpoint_file.exists():
            return None

        with open(checkpoint_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def list_checkpoints(self, doc_id: str) -> list:
        """문서의 모든 체크포인트 목록"""
        checkpoints = []

        for file in self.checkpoint_dir.glob(f"{doc_id}_*.json"):
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                checkpoints.append(data)

        return sorted(checkpoints, key=lambda x: x['timestamp'])

    def delete_checkpoint(self, doc_id: str, stage: str) -> bool:
        """체크포인트 삭제"""
        checkpoint_file = self.checkpoint_dir / f"{doc_id}_{stage}.json"

        if checkpoint_file.exists():
            checkpoint_file.unlink()
            return True

        return False

    def delete_all_checkpoints(self, doc_id: str) -> int:
        """문서의 모든 체크포인트 삭제"""
        count = 0
        for file in self.checkpoint_dir.glob(f"{doc_id}_*.json"):
            file.unlink()
            count += 1

        return count

    def get_latest_checkpoint(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """최신 체크포인트 조회"""
        checkpoints = self.list_checkpoints(doc_id)
        return checkpoints[-1] if checkpoints else None

    def clear_old_checkpoints(self, doc_id: str, keep_last: int = 3) -> int:
        """오래된 체크포인트 정리"""
        checkpoints = self.list_checkpoints(doc_id)

        if len(checkpoints) <= keep_last:
            return 0

        to_delete = checkpoints[:-keep_last]
        deleted = 0

        for checkpoint in to_delete:
            if self.delete_checkpoint(doc_id, checkpoint['stage']):
                deleted += 1

        return deleted

    def create_backup(self, doc_id: str) -> str:
        """전체 상태 백업 (피클 형식)"""
        checkpoints = self.list_checkpoints(doc_id)

        backup_file = self.checkpoint_dir / f"{doc_id}_backup.pkl"

        with open(backup_file, 'wb') as f:
            pickle.dump(checkpoints, f)

        return str(backup_file)

    def restore_backup(self, doc_id: str) -> Optional[list]:
        """백업에서 복구"""
        backup_file = self.checkpoint_dir / f"{doc_id}_backup.pkl"

        if not backup_file.exists():
            return None

        with open(backup_file, 'rb') as f:
            return pickle.load(f)

    def get_progress_summary(self, doc_id: str) -> Dict[str, Any]:
        """진행 상황 요약"""
        checkpoints = self.list_checkpoints(doc_id)

        stages = set()
        for cp in checkpoints:
            stages.add(cp['stage'])

        return {
            'doc_id': doc_id,
            'total_checkpoints': len(checkpoints),
            'stages_completed': sorted(list(stages)),
            'latest_stage': checkpoints[-1]['stage'] if checkpoints else None,
            'latest_timestamp': checkpoints[-1]['timestamp'] if checkpoints else None,
        }
