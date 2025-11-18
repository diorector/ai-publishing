# 윤문 모듈
# 작성일: 2025-11-18
# 목적: 문체 통일, 문장 개선, 가독성 최적화, 저자 의도 보존

import re
import time
from typing import Dict, List, Any, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from collections import Counter

from .models.edit_result import EditResult, EditStage, Change


@dataclass
class ImprovementRecord:
    """개선 기록"""
    type: str
    original: str
    improved: str
    reason: str
    position: int = 0
    confidence: float = 0.9


class CopywritingModule:
    """윤문 모듈 - 문체 통일, 문장 개선, 가독성 최적화"""

    # 번역체 표현 패턴
    TRANSLATION_PATTERNS = [
        (r'~(?:할\s)?수\s+있다', '~할 수 있다'),
        (r'~(?:하)는\s+바이다', '~한다'),
        (r'~(?:하)는\s+바이다', '~이다'),
        (r'~라는\s+점이\s+있다', '~이다'),
        (r'~한다는\s+점', '~한 점'),
    ]

    # 어색한 표현 패턴
    AWKWARD_PATTERNS = {
        '되어지다': '되다',
        '이루어지다': '이루어진다',
        '생각된다': '생각한다',
        '알려진다': '알려진다',
    }

    # 반복된 단어 패턴
    COMMON_REPETITIONS = [
        r'(매우|정말|사실)\s+\1',
        r'(이\s+)?(\w+)\s+(\w+)\s+\2',
    ]

    # 단어 반복 제한 (단어가 N번 이상 반복되면 개선 필요)
    WORD_REPETITION_THRESHOLD = 4

    # 존댓말 패턴
    HONORIFIC_PATTERNS = {
        'ending_formal': [r'습니다$', r'입니다$', r'합니다$'],
        'ending_casual': [r'해요$', r'해$', r'어요$'],
        'honorific_formal': [r'세$', r'신$'],
        'honorific_casual': [r'(으)로$'],
    }

    # 비격식/격식 지표
    INFORMALITY_INDICATORS = [
        '막', '그냥', '그럼', '아무튼', '어쨌든',
    ]

    # 기술 용어와 일반 표현의 균형
    TECHNICAL_TERMS = {
        '알고리즘': '방법',
        '구현': '만들기',
        '최적화': '더 나은 버전',
        '메커니즘': '작동 방식',
        '파라미터': '매개변수',
    }

    def __init__(self):
        """초기화"""
        self.improvements: List[ImprovementRecord] = []

    def improve_sentence(self, sentence: str) -> Dict[str, Any]:
        """단일 문장 개선"""
        if not sentence or not sentence.strip():
            raise ValueError("문장이 비어있습니다")

        improvements = []
        improved = sentence

        # 문장 길이 확인 (40-50자 이상이면 분해 필요)
        if len(improved) > 50:
            # 복문 분해 패턴 찾기
            split_result = self._split_complex_sentence(improved)
            if split_result:
                improvements.append({
                    'type': 'sentence_simplification',
                    'original': improved,
                    'improved': split_result,
                    'reason': '길고 복잡한 문장을 단순화함'
                })
                improved = split_result

        # 수동태 → 능동태 변환
        active_result = self._convert_passive_to_active(improved)
        if active_result != improved:
            improvements.append({
                'type': 'voice_conversion',
                'original': improved,
                'improved': active_result,
                'reason': '수동태를 능동태로 변경'
            })
            improved = active_result

        # 모호한 대명사 명확화
        pronoun_result = self._clarify_pronouns(improved)
        if pronoun_result != improved:
            improvements.append({
                'type': 'pronoun_clarification',
                'original': improved,
                'improved': pronoun_result,
                'reason': '모호한 대명사를 명확히 함'
            })
            improved = pronoun_result

        return {
            'improved_text': improved,
            'improvements': improvements,
            'changes_count': len(improvements),
            'original_length': len(sentence),
            'improved_length': len(improved),
        }

    def _split_complex_sentence(self, sentence: str) -> Optional[str]:
        """복문을 단문으로 분해"""
        # 접속사 패턴을 찾아 문장 분해
        separators = ['하지만', '그러나', '그래서', '따라서', '그로인해', '그러므로', '그리고', '또한']

        for sep in separators:
            if sep in sentence:
                # 접속사 기준으로 분해
                parts = sentence.split(sep)
                if len(parts) > 1:
                    # 각 부분에 종결어미 추가
                    result = f"{parts[0].strip()}. {sep} {parts[1].strip()}."
                    return result

        return None

    def _convert_passive_to_active(self, text: str) -> str:
        """수동태를 능동태로 변경"""
        conversions = [
            (r'(\w+)에\s+의해\s+(\w+)되었다', r'\2가 \1하였다'),
            (r'(\w+)에\s+의해\s+(\w+)하였다', r'\2가 \1하였다'),
        ]

        result = text
        for pattern, replacement in conversions:
            result = re.sub(pattern, replacement, result)

        return result

    def _clarify_pronouns(self, text: str) -> str:
        """모호한 대명사 명확화"""
        # 기본적인 대명사 명확화는 LLM이 필요하므로, 여기서는 스텁
        return text

    def check_tone_consistency(self, text: str) -> Dict[str, Any]:
        """문체 일관성 검증"""
        lines = text.split('\n')
        formal_count = 0
        casual_count = 0
        issues = []

        for line in lines:
            if not line.strip():
                continue

            # 존댓말 형태 감지
            if re.search(r'습니다$|입니다$|합니다$', line):
                formal_count += 1
            elif re.search(r'해요$|해$|어요$', line):
                casual_count += 1

        # 일관성 점수 계산
        total = formal_count + casual_count
        if total > 0:
            consistency_score = 100 - (abs(formal_count - casual_count) / total * 100)
        else:
            consistency_score = 100

        if formal_count > 0 and casual_count > 0:
            issues.append({
                'type': 'mixed_formality',
                'count': min(formal_count, casual_count),
                'description': '존댓말과 반말이 섞여있습니다'
            })

        return {
            'consistency_score': max(0, consistency_score),
            'formal_lines': formal_count,
            'casual_lines': casual_count,
            'issues': issues,
        }

    def analyze_readability(self, text: str) -> Dict[str, Any]:
        """가독성 분석"""
        words = re.findall(r'\w+', text)
        word_freq = Counter(words)

        # 반복되는 단어 찾기
        repeated_words = {word: count for word, count in word_freq.items()
                         if count >= self.WORD_REPETITION_THRESHOLD}

        # 평균 문장 길이
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        avg_sentence_length = len(text) / len(sentences) if sentences else 0

        # 가독성 점수 (간단한 휴리스틱)
        readability_score = 100
        if avg_sentence_length > 50:
            readability_score -= 20
        if len(repeated_words) > 5:
            readability_score -= 15

        return {
            'repeated_words': repeated_words,
            'average_sentence_length': avg_sentence_length,
            'sentence_count': len(sentences),
            'readability_score': max(0, readability_score),
            'total_words': len(words),
            'unique_words': len(word_freq),
        }

    def improve_paragraph(self, paragraph: str, context: str = None) -> Dict[str, Any]:
        """단락 개선"""
        if not paragraph or not paragraph.strip():
            raise ValueError("단락이 비어있습니다")

        start_time = time.time()
        improvements = []
        improved = paragraph

        # 번역체 표현 제거
        translation_result = self._remove_translation_style(improved)
        if translation_result != improved:
            improvements.append({
                'type': 'translation_style_removal',
                'original': improved,
                'improved': translation_result,
                'reason': '번역체 표현을 제거하고 자연스러운 한국어로 변경'
            })
            improved = translation_result

        # 어색한 표현 개선
        awkward_result = self._improve_awkward_phrasing(improved)
        if awkward_result != improved:
            improvements.append({
                'type': 'awkward_phrasing_improvement',
                'original': improved,
                'improved': awkward_result,
                'reason': '어색한 표현을 더 자연스럽게 변경'
            })
            improved = awkward_result

        # 가독성 개선
        readability_improvements = self._improve_readability(improved)
        if readability_improvements['improved_text'] != improved:
            improvements.append({
                'type': 'readability_improvement',
                'original': improved,
                'improved': readability_improvements['improved_text'],
                'reason': '단어 반복을 줄이고 논리적 흐름을 개선'
            })
            improved = readability_improvements['improved_text']

        processing_time = time.time() - start_time

        # 가독성 변화도 계산
        original_metrics = self.analyze_readability(paragraph)
        improved_metrics = self.analyze_readability(improved)
        readability_change = improved_metrics['readability_score'] - original_metrics['readability_score']

        # 품질 점수
        quality_score = 85.0 + min(readability_change, 15)

        return {
            'improved_text': improved,
            'changes': improvements,
            'quality_score': min(quality_score, 100),
            'readability_change': readability_change,
            'processing_time': processing_time,
        }

    def _remove_translation_style(self, text: str) -> str:
        """번역체 표현 제거"""
        result = text
        for pattern, replacement in self.TRANSLATION_PATTERNS:
            result = re.sub(pattern, replacement, result)
        return result

    def _improve_awkward_phrasing(self, text: str) -> str:
        """어색한 표현 개선"""
        result = text
        for awkward, natural in self.AWKWARD_PATTERNS.items():
            result = result.replace(awkward, natural)
        return result

    def _improve_readability(self, text: str) -> Dict[str, Any]:
        """가독성 개선"""
        # 단어 반복도 분석
        words = re.findall(r'\w+', text)
        word_freq = Counter(words)
        repeated = [w for w, c in word_freq.items() if c >= 3]

        improved = text
        for word in repeated:
            # 반복되는 단어를 의동사나 대명사로 치환 (간단한 로직)
            if word in self.TECHNICAL_TERMS:
                # 기술 용어는 첫 번째만 유지하고 나머지는 '이'나 '그것'으로 치환
                pattern = rf'\b{word}\b'
                occurrences = list(re.finditer(pattern, improved))
                if len(occurrences) > 1:
                    # 두 번째 이후는 '이'로 치환
                    temp = improved
                    for i, match in enumerate(occurrences[1:], 1):
                        temp = temp[:match.start()] + '이' + temp[match.end():]

        return {
            'improved_text': improved,
            'repeated_words': repeated,
        }

    def calculate_readability_metrics(self, text: str) -> Dict[str, Any]:
        """가독성 지표 계산"""
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]

        if not sentences:
            return {'readability_score': 0}

        # 평균 문장 길이
        total_chars = sum(len(s) for s in sentences)
        avg_sentence_length = total_chars / len(sentences)

        # 평균 단어 길이
        words = re.findall(r'\w+', text)
        avg_word_length = sum(len(w) for w in words) / len(words) if words else 0

        # 가독성 점수 (간단한 공식)
        # 문장이 짧을수록, 단어가 짧을수록 가독성이 높음
        readability_score = 100
        if avg_sentence_length > 50:
            readability_score -= (avg_sentence_length - 50) / 2
        if avg_word_length > 5:
            readability_score -= (avg_word_length - 5) * 2

        return {
            'readability_score': max(0, readability_score),
            'average_sentence_length': avg_sentence_length,
            'average_word_length': avg_word_length,
            'sentence_count': len(sentences),
        }

    def calculate_coherence_score(self, text: str) -> Dict[str, Any]:
        """일관성 점수 계산"""
        # 연결사 사용도 분석
        connectors = [
            '첫째', '두번째', '세번째',
            '우선', '다음', '마지막',
            '따라서', '그러므로', '그래서',
            '그러나', '하지만', '그렇지만'
        ]

        connector_count = sum(1 for conn in connectors if conn in text)

        # 논리적 흐름 평가 (간단한 휴리스틱)
        coherence_score = 50 + (connector_count * 5)
        coherence_score = min(coherence_score, 100)

        return {
            'coherence_score': coherence_score,
            'connector_count': connector_count,
        }

    def calculate_tone_consistency_score(self, text: str) -> Dict[str, Any]:
        """문체 일관성 점수"""
        consistency_result = self.check_tone_consistency(text)
        return {
            'tone_score': consistency_result['consistency_score'],
            'issues': consistency_result['issues'],
        }

    def copywrite(self, text: str, domain: str = "general", target_audience: str = "general") -> Dict[str, Any]:
        """전체 윤문 프로세스"""
        if not text or not text.strip():
            raise ValueError("텍스트가 비어있습니다")

        start_time = time.time()

        # 단락별로 분할
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]

        improved_paragraphs = []
        all_improvements = []

        for para in paragraphs:
            para_result = self.improve_paragraph(para)
            improved_paragraphs.append(para_result['improved_text'])
            all_improvements.extend(para_result['changes'])

        improved_text = '\n\n'.join(improved_paragraphs)

        # 문체 일관성 검증
        tone_result = self.check_tone_consistency(improved_text)

        # 가독성 평가
        readability_result = self.calculate_readability_metrics(improved_text)

        processing_time = time.time() - start_time

        # 품질 점수 계산
        quality_score = 85.0
        quality_score += min(tone_result['consistency_score'] - 75, 15) / 15
        quality_score += min(readability_result['readability_score'] - 50, 15) / 15

        return {
            'improved_text': improved_text,
            'changes': all_improvements,
            'quality_score': min(quality_score, 100),
            'tone_consistency': tone_result['consistency_score'],
            'readability': readability_result['readability_score'],
            'processing_time': processing_time,
            'paragraph_count': len(paragraphs),
        }

    def copywrite_parallel(self, text: str, max_workers: int = 10) -> Dict[str, Any]:
        """병렬 윤문"""
        start_time = time.time()

        # 단락별로 분할
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]

        improved_paragraphs = []
        all_improvements = []

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(self.improve_paragraph, para): idx
                for idx, para in enumerate(paragraphs)
            }

            for future in as_completed(futures):
                idx = futures[future]
                result = future.result()
                improved_paragraphs.append((idx, result['improved_text']))
                all_improvements.extend(result['changes'])

        # 원래 순서대로 정렬
        improved_paragraphs.sort(key=lambda x: x[0])
        improved_text = '\n\n'.join([p[1] for p in improved_paragraphs])

        processing_time = time.time() - start_time

        return {
            'improved_text': improved_text,
            'changes': all_improvements,
            'quality_score': 85.0,
            'processing_time': processing_time,
            'paragraph_count': len(paragraphs),
        }
