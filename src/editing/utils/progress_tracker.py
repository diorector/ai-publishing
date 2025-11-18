# 진행률 추적 유틸리티
# 작성일: 2025-11-18
# 목적: 편집 진행 상황 실시간 추적

from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
import time


class ProgressTracker:
    """편집 진행률 추적"""

    def __init__(self, total_documents: int = 1):
        """초기화"""
        self.total_documents = total_documents
        self.current_document = 0
        self.documents_progress: Dict[int, Dict[str, Any]] = {}
        self.callbacks: List[Callable] = []
        self.start_time = time.time()

    def start_document(self, doc_id: str, doc_name: str, stages: List[str]):
        """문서 처리 시작"""
        self.current_document += 1
        self.documents_progress[self.current_document] = {
            'doc_id': doc_id,
            'doc_name': doc_name,
            'stages': stages,
            'current_stage': 0,
            'total_stages': len(stages),
            'start_time': time.time(),
            'status': 'processing',
        }
        self._notify_progress()

    def update_stage(self, stage: str, progress: float):
        """단계 진행률 업데이트"""
        if self.current_document in self.documents_progress:
            doc = self.documents_progress[self.current_document]
            if stage in doc['stages']:
                doc['current_stage'] = doc['stages'].index(stage) + 1
                doc['stage_progress'] = progress
            self._notify_progress()

    def complete_stage(self, stage: str):
        """단계 완료"""
        if self.current_document in self.documents_progress:
            doc = self.documents_progress[self.current_document]
            if stage in doc['stages']:
                doc['current_stage'] = doc['stages'].index(stage) + 1
            self._notify_progress()

    def complete_document(self):
        """문서 처리 완료"""
        if self.current_document in self.documents_progress:
            doc = self.documents_progress[self.current_document]
            doc['status'] = 'completed'
            doc['end_time'] = time.time()
        self._notify_progress()

    def add_callback(self, callback: Callable):
        """진행률 콜백 추가"""
        self.callbacks.append(callback)

    def get_progress(self) -> Dict[str, Any]:
        """현재 진행 상황 조회"""
        elapsed = time.time() - self.start_time
        estimated_total = self._estimate_total_time()

        return {
            'documents_completed': sum(
                1 for d in self.documents_progress.values()
                if d['status'] == 'completed'
            ),
            'documents_total': self.total_documents,
            'current_document': self.current_document,
            'elapsed_time': elapsed,
            'estimated_total_time': estimated_total,
            'estimated_remaining': max(0, estimated_total - elapsed),
            'overall_progress': self._calculate_overall_progress(),
            'document_progress': self.documents_progress.get(self.current_document, {}),
        }

    def _calculate_overall_progress(self) -> float:
        """전체 진행률 계산"""
        if not self.documents_progress:
            return 0.0

        total_stage_progress = 0
        for doc in self.documents_progress.values():
            stage_progress = doc['current_stage'] / doc['total_stages'] * 100
            total_stage_progress += stage_progress

        overall = total_stage_progress / len(self.documents_progress)
        return min(overall, 100)

    def _estimate_total_time(self) -> float:
        """예상 총 소요 시간 계산"""
        if not self.documents_progress or self.current_document == 0:
            return 0

        completed = sum(
            (d['end_time'] - d['start_time'])
            for d in self.documents_progress.values()
            if d['status'] == 'completed'
        )

        if self.current_document > 0:
            avg_time = completed / self.current_document
            estimated = avg_time * self.total_documents
            return estimated

        return 0

    def _notify_progress(self):
        """진행률 알림"""
        progress = self.get_progress()
        for callback in self.callbacks:
            try:
                callback(progress)
            except:
                pass

    def print_summary(self):
        """진행 상황 요약 출력"""
        progress = self.get_progress()
        print(f"\n====== 진행 상황 ======")
        print(f"완료: {progress['documents_completed']}/{progress['documents_total']}")
        print(f"진행률: {progress['overall_progress']:.1f}%")
        print(f"소요 시간: {progress['elapsed_time']:.1f}초")
        print(f"예상 남은 시간: {progress['estimated_remaining']:.1f}초")
        print(f"======================\n")
