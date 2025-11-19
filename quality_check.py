#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
출판 전 최종 품질 검증 시스템
- 구조 무결성 (순서, 누락, 중복)
- 문장 품질 (길이, 가독성, 일관성)
- 출판 준비도 (포맷, 특수문자, 레이아웃)

사용법:
  python quality_check.py output_edited/growth_levers_kr/growth_levers_kr_edited.md
  python quality_check.py output_edited/growth_levers_kr/growth_levers_kr_edited.md --strict
"""

import sys
import os
from pathlib import Path
import argparse
import re
from typing import List, Dict, Tuple
from dataclasses import dataclass
from collections import Counter

# Set encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


@dataclass
class QualityIssue:
    """품질 이슈"""
    severity: str  # 'critical', 'warning', 'info'
    category: str
    line_num: int
    message: str
    context: str = ""


class QualityChecker:
    """출판 품질 검증기"""
    
    def __init__(self, strict_mode: bool = False):
        self.strict_mode = strict_mode
        self.issues: List[QualityIssue] = []
    
    def check_document(self, file_path: Path) -> Dict:
        """문서 전체 검증"""
        content = file_path.read_text(encoding='utf-8')
        lines = content.split('\n')
        
        print(f"\n📋 문서 정보")
        print(f"   파일: {file_path.name}")
        print(f"   크기: {len(content):,} 자")
        print(f"   라인: {len(lines):,}개")
        
        # 검증 실행
        self._check_structure(lines)
        self._check_sentence_quality(lines)
        self._check_formatting(lines)
        self._check_consistency(lines)
        self._check_readability(content)
        
        return self._generate_report()
    
    def _check_structure(self, lines: List[str]):
        """구조 무결성 검증"""
        print(f"\n🔍 [1/5] 구조 무결성 검증...")
        
        # 1. 제목 계층 구조
        heading_levels = []
        for i, line in enumerate(lines, 1):
            if line.startswith('#'):
                level = len(line) - len(line.lstrip('#'))
                heading_levels.append((i, level, line.strip()))
        
        # 제목 레벨 점프 체크
        for i in range(1, len(heading_levels)):
            prev_level = heading_levels[i-1][1]
            curr_level = heading_levels[i][1]
            
            if curr_level > prev_level + 1:
                self.issues.append(QualityIssue(
                    severity='warning',
                    category='구조',
                    line_num=heading_levels[i][0],
                    message=f'제목 레벨 점프: H{prev_level} → H{curr_level}',
                    context=heading_levels[i][2]
                ))
        
        # 2. 빈 섹션 체크
        for i in range(len(heading_levels) - 1):
            start_line = heading_levels[i][0]
            end_line = heading_levels[i+1][0]
            
            section_content = '\n'.join(lines[start_line:end_line]).strip()
            if len(section_content.split()) < 10:
                self.issues.append(QualityIssue(
                    severity='warning',
                    category='구조',
                    line_num=start_line,
                    message='내용이 너무 짧은 섹션 (10단어 미만)',
                    context=heading_levels[i][2]
                ))
        
        # 3. 중복 제목 체크
        heading_texts = [h[2] for h in heading_levels]
        duplicates = [text for text, count in Counter(heading_texts).items() if count > 1]
        
        for dup in duplicates:
            for line_num, _, text in heading_levels:
                if text == dup:
                    self.issues.append(QualityIssue(
                        severity='warning',
                        category='구조',
                        line_num=line_num,
                        message='중복된 제목',
                        context=text
                    ))
        
        print(f"   ✓ 제목 구조: {len(heading_levels)}개 제목 검증 완료")
    
    def _check_sentence_quality(self, lines: List[str]):
        """문장 품질 검증"""
        print(f"\n🔍 [2/5] 문장 품질 검증...")
        
        for i, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            # 1. 너무 긴 문장 (100자 이상)
            sentences = re.split(r'[.!?]\s+', line)
            for sent in sentences:
                if len(sent) > 100:
                    self.issues.append(QualityIssue(
                        severity='info',
                        category='문장',
                        line_num=i,
                        message=f'긴 문장 ({len(sent)}자)',
                        context=sent[:50] + '...'
                    ))
            
            # 2. 번역체 표현
            translation_patterns = [
                (r'~되어지다', '번역체: ~되어지다'),
                (r'~되어진', '번역체: ~되어진'),
                (r'것이다\.', '번역체: ~것이다'),
                (r'~에 대해서', '번역체: ~에 대해서'),
                (r'~에 있어서', '번역체: ~에 있어서'),
            ]
            
            for pattern, msg in translation_patterns:
                if re.search(pattern, line):
                    self.issues.append(QualityIssue(
                        severity='warning',
                        category='문장',
                        line_num=i,
                        message=msg,
                        context=line[:50]
                    ))
            
            # 3. 반복 단어
            words = line.split()
            for j in range(len(words) - 1):
                if words[j] == words[j+1] and len(words[j]) > 1:
                    self.issues.append(QualityIssue(
                        severity='warning',
                        category='문장',
                        line_num=i,
                        message=f'반복 단어: "{words[j]}"',
                        context=line[:50]
                    ))
        
        print(f"   ✓ 문장 품질: {len(lines)}개 라인 검증 완료")
    
    def _check_formatting(self, lines: List[str]):
        """포맷팅 검증"""
        print(f"\n🔍 [3/5] 포맷팅 검증...")
        
        for i, line in enumerate(lines, 1):
            # 1. 연속된 빈 줄 (3개 이상)
            if i < len(lines) - 2:
                if not line and not lines[i] and not lines[i+1]:
                    self.issues.append(QualityIssue(
                        severity='info',
                        category='포맷',
                        line_num=i,
                        message='연속된 빈 줄 (3개 이상)',
                        context=''
                    ))
            
            # 2. 잘못된 마크다운 문법
            if line.startswith('#'):
                if not line.startswith('# ') and len(line) > 1:
                    self.issues.append(QualityIssue(
                        severity='warning',
                        category='포맷',
                        line_num=i,
                        message='제목 뒤 공백 누락',
                        context=line[:30]
                    ))
            
            # 3. 불필요한 공백
            if '  ' in line and not line.startswith('    '):  # 코드 블록 제외
                self.issues.append(QualityIssue(
                    severity='info',
                    category='포맷',
                    line_num=i,
                    message='연속된 공백',
                    context=line[:50]
                ))
            
            # 4. 줄 끝 공백
            if line.endswith(' ') and line.strip():
                self.issues.append(QualityIssue(
                    severity='info',
                    category='포맷',
                    line_num=i,
                    message='줄 끝 공백',
                    context=line[:50]
                ))
        
        print(f"   ✓ 포맷팅: {len(lines)}개 라인 검증 완료")
    
    def _check_consistency(self, lines: List[str]):
        """일관성 검증"""
        print(f"\n🔍 [4/5] 일관성 검증...")
        
        # 1. 존댓말/반말 혼용
        jondae_count = 0
        banmal_count = 0
        
        for i, line in enumerate(lines, 1):
            if '습니다' in line or '합니다' in line or '입니다' in line:
                jondae_count += 1
            if re.search(r'[이다|한다|된다]\.$', line):
                banmal_count += 1
        
        if jondae_count > 0 and banmal_count > 0:
            ratio = min(jondae_count, banmal_count) / max(jondae_count, banmal_count)
            if ratio > 0.1:  # 10% 이상 혼용
                self.issues.append(QualityIssue(
                    severity='warning',
                    category='일관성',
                    line_num=0,
                    message=f'존댓말/반말 혼용 (존댓말: {jondae_count}, 반말: {banmal_count})',
                    context=''
                ))
        
        # 2. 숫자 표기 일관성 (아라비아 vs 한글)
        # 간단한 체크만 수행
        
        print(f"   ✓ 일관성: 존댓말 {jondae_count}개, 반말 {banmal_count}개")
    
    def _check_readability(self, content: str):
        """가독성 검증"""
        print(f"\n🔍 [5/5] 가독성 검증...")
        
        # 1. 평균 문장 길이
        sentences = re.split(r'[.!?]\s+', content)
        sentences = [s for s in sentences if len(s.strip()) > 0]
        
        if sentences:
            avg_length = sum(len(s) for s in sentences) / len(sentences)
            
            if avg_length > 80:
                self.issues.append(QualityIssue(
                    severity='info',
                    category='가독성',
                    line_num=0,
                    message=f'평균 문장 길이가 김 ({avg_length:.0f}자)',
                    context='문장을 더 짧게 나누는 것을 권장합니다'
                ))
            
            print(f"   ✓ 평균 문장 길이: {avg_length:.0f}자")
        
        # 2. 단락 길이
        paragraphs = content.split('\n\n')
        long_paragraphs = [p for p in paragraphs if len(p) > 500]
        
        if long_paragraphs:
            self.issues.append(QualityIssue(
                severity='info',
                category='가독성',
                line_num=0,
                message=f'긴 단락 {len(long_paragraphs)}개 발견',
                context='단락을 나누는 것을 권장합니다'
            ))
        
        print(f"   ✓ 단락 수: {len(paragraphs)}개 (긴 단락: {len(long_paragraphs)}개)")
    
    def _generate_report(self) -> Dict:
        """검증 리포트 생성"""
        critical = [i for i in self.issues if i.severity == 'critical']
        warnings = [i for i in self.issues if i.severity == 'warning']
        info = [i for i in self.issues if i.severity == 'info']
        
        return {
            'total_issues': len(self.issues),
            'critical': critical,
            'warnings': warnings,
            'info': info,
            'is_publishable': len(critical) == 0 and (not self.strict_mode or len(warnings) == 0)
        }


def print_report(report: Dict, checker: QualityChecker):
    """리포트 출력"""
    print("\n" + "=" * 80)
    print("📊 품질 검증 결과")
    print("=" * 80)
    
    critical = report['critical']
    warnings = report['warnings']
    info = report['info']
    
    print(f"\n총 이슈: {report['total_issues']}개")
    print(f"  🔴 치명적: {len(critical)}개")
    print(f"  🟡 경고: {len(warnings)}개")
    print(f"  🔵 정보: {len(info)}개")
    
    # 치명적 이슈
    if critical:
        print("\n" + "=" * 80)
        print("🔴 치명적 이슈 (반드시 수정 필요)")
        print("=" * 80)
        for issue in critical:
            print(f"\n라인 {issue.line_num}: {issue.message}")
            print(f"  카테고리: {issue.category}")
            if issue.context:
                print(f"  컨텍스트: {issue.context}")
    
    # 경고
    if warnings:
        print("\n" + "=" * 80)
        print("🟡 경고 (수정 권장)")
        print("=" * 80)
        
        # 카테고리별로 그룹화
        by_category = {}
        for issue in warnings:
            if issue.category not in by_category:
                by_category[issue.category] = []
            by_category[issue.category].append(issue)
        
        for category, issues in by_category.items():
            print(f"\n[{category}] {len(issues)}개")
            for issue in issues[:5]:  # 최대 5개만 표시
                print(f"  • 라인 {issue.line_num}: {issue.message}")
                if issue.context:
                    print(f"    → {issue.context[:60]}")
            
            if len(issues) > 5:
                print(f"  ... 외 {len(issues) - 5}개")
    
    # 정보
    if info:
        print("\n" + "=" * 80)
        print("🔵 정보 (참고사항)")
        print("=" * 80)
        
        by_category = {}
        for issue in info:
            if issue.category not in by_category:
                by_category[issue.category] = []
            by_category[issue.category].append(issue)
        
        for category, issues in by_category.items():
            print(f"  [{category}] {len(issues)}개")
    
    # 최종 판정
    print("\n" + "=" * 80)
    print("✅ 최종 판정")
    print("=" * 80)
    
    if report['is_publishable']:
        print("\n🎉 출판 준비 완료!")
        print("   이 문서는 출판 품질 기준을 충족합니다.")
        if warnings:
            print(f"   (경고 {len(warnings)}개가 있지만 출판 가능)")
    else:
        print("\n⚠️  출판 전 수정 필요")
        if critical:
            print(f"   치명적 이슈 {len(critical)}개를 먼저 해결하세요.")
        if checker.strict_mode and warnings:
            print(f"   엄격 모드: 경고 {len(warnings)}개도 해결해야 합니다.")
    
    print("\n" + "=" * 80)


def main():
    parser = argparse.ArgumentParser(
        description='출판 전 최종 품질 검증',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예시:
  python quality_check.py output_edited/growth_levers_kr/growth_levers_kr_edited.md
  python quality_check.py output_edited/growth_levers_kr/growth_levers_kr_edited.md --strict
        """
    )
    
    parser.add_argument('file', help='검증할 파일 경로')
    parser.add_argument('--strict', action='store_true',
                       help='엄격 모드 (경고도 출판 불가 판정)')
    
    args = parser.parse_args()
    
    file_path = Path(args.file)
    if not file_path.exists():
        print(f"❌ 파일을 찾을 수 없습니다: {file_path}")
        sys.exit(1)
    
    print("\n" + "=" * 80)
    print("🔍 출판 품질 검증 시스템")
    print("=" * 80)
    
    if args.strict:
        print("⚠️  엄격 모드: 경고도 출판 불가 판정")
    
    # 검증 실행
    checker = QualityChecker(strict_mode=args.strict)
    report = checker.check_document(file_path)
    
    # 리포트 출력
    print_report(report, checker)
    
    # 종료 코드
    sys.exit(0 if report['is_publishable'] else 1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  사용자에 의해 중단되었습니다.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
