# 배치 처리 유틸리티
# 작성일: 2025-11-18
# 목적: 여러 문서 순차/병렬 처리

from typing import List, Dict, Any, Optional, Callable
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import time


class BatchProcessor:
    """배치 문서 처리"""

    def __init__(self, max_workers: int = 1):
        """초기화"""
        self.max_workers = max_workers
        self.results: List[Dict[str, Any]] = []
        self.progress_callback: Optional[Callable] = None

    def set_progress_callback(self, callback: Callable) -> None:
        """진행률 콜백 설정"""
        self.progress_callback = callback

    def process_sequential(
        self,
        items: List[Any],
        processor: Callable,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """순차 처리"""
        results = []

        for i, item in enumerate(items):
            try:
                result = processor(item, **kwargs)
                results.append({
                    'item': item,
                    'status': 'success',
                    'result': result,
                })
            except Exception as e:
                results.append({
                    'item': item,
                    'status': 'error',
                    'error': str(e),
                })

            # 진행률 콜백
            if self.progress_callback:
                progress = (i + 1) / len(items) * 100
                self.progress_callback(progress, item)

        return results

    def process_parallel(
        self,
        items: List[Any],
        processor: Callable,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """병렬 처리"""
        results = []
        completed = 0

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(processor, item, **kwargs): i
                for i, item in enumerate(items)
            }

            for future in as_completed(futures):
                idx = futures[future]
                item = items[idx]

                try:
                    result = future.result()
                    results.append({
                        'item': item,
                        'status': 'success',
                        'result': result,
                    })
                except Exception as e:
                    results.append({
                        'item': item,
                        'status': 'error',
                        'error': str(e),
                    })

                completed += 1

                # 진행률 콜백
                if self.progress_callback:
                    progress = completed / len(items) * 100
                    self.progress_callback(progress, item)

        return results

    def process_chunked(
        self,
        items: List[Any],
        processor: Callable,
        chunk_size: int = 10,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """청크 단위 처리"""
        results = []
        total_items = len(items)

        for chunk_start in range(0, total_items, chunk_size):
            chunk_end = min(chunk_start + chunk_size, total_items)
            chunk = items[chunk_start:chunk_end]

            try:
                result = processor(chunk, **kwargs)
                for item in chunk:
                    results.append({
                        'item': item,
                        'status': 'success',
                        'result': result,
                    })
            except Exception as e:
                for item in chunk:
                    results.append({
                        'item': item,
                        'status': 'error',
                        'error': str(e),
                    })

            # 진행률 콜백
            if self.progress_callback:
                progress = chunk_end / total_items * 100
                self.progress_callback(progress, None)

        return results

    def get_summary(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """처리 결과 요약"""
        successful = sum(1 for r in results if r['status'] == 'success')
        failed = sum(1 for r in results if r['status'] == 'error')

        return {
            'total': len(results),
            'successful': successful,
            'failed': failed,
            'success_rate': (successful / len(results) * 100) if results else 0,
            'errors': [r.get('error') for r in results if r['status'] == 'error'],
        }

    def filter_results(
        self,
        results: List[Dict[str, Any]],
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """결과 필터링"""
        if status:
            return [r for r in results if r['status'] == status]
        return results

    def retry_failed(
        self,
        results: List[Dict[str, Any]],
        processor: Callable,
        max_retries: int = 3,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """실패한 항목 재처리"""
        failed_items = [r for r in results if r['status'] == 'error']
        retried_results = []

        for item_data in failed_items:
            item = item_data['item']
            retries = 0

            while retries < max_retries:
                try:
                    result = processor(item, **kwargs)
                    retried_results.append({
                        'item': item,
                        'status': 'success',
                        'result': result,
                        'retries': retries,
                    })
                    break
                except Exception as e:
                    retries += 1
                    if retries >= max_retries:
                        retried_results.append({
                            'item': item,
                            'status': 'error',
                            'error': str(e),
                            'retries': retries,
                        })

        return retried_results
