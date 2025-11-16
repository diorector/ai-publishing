# PDF 추출 및 번역 테스트 스크립트
# 사용: python test_pdf_extract.py

from pathlib import Path
import sys

# PDF 처리 함수
def extract_pdf_simple(pdf_path):
    """PDF에서 텍스트 추출 (간단 버전)"""
    try:
        import pdfplumber

        with pdfplumber.open(pdf_path) as pdf:
            text = ""
            metadata = pdf.metadata
            pages = []

            print(f"📖 PDF 정보:")
            print(f"   페이지: {len(pdf.pages)}")
            if metadata:
                print(f"   제목: {metadata.get('Title', '없음')}")
                print(f"   저자: {metadata.get('Author', '없음')}")
            print()

            for i, page in enumerate(pdf.pages):
                page_text = page.extract_text()
                text += page_text + "\n"
                pages.append(page_text)

            return text, metadata, pages

    except ImportError:
        print("❌ pdfplumber 미설치")
        print("설치: pip install pdfplumber")
        return None, None, None


def chunk_text(text, chunk_size=5000):
    """텍스트를 청크로 나누기"""
    chunks = []
    words = text.split()
    current_chunk = []
    current_size = 0

    for word in words:
        current_size += len(word) + 1
        current_chunk.append(word)

        if current_size >= chunk_size:
            chunks.append(" ".join(current_chunk))
            current_chunk = []
            current_size = 0

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks


def mock_translate(text, source="English", target="Korean"):
    """모의 번역 (실제 번역 없이 마킹만)"""
    # 간단한 프리뷰: 원문 + [번역됨] 표시
    lines = text.split('\n')
    translated_lines = []

    for line in lines:
        if line.strip():
            # 간단한 "번역" 처리: 단어 순서 약간 섞기
            words = line.split()
            if len(words) > 3:
                # 단어 일부를 재배열하여 "번역된" 것처럼 표현
                translated_lines.append(f"[KOR] {line[:50]}...")
            else:
                translated_lines.append(f"[KOR] {line}")
        else:
            translated_lines.append("")

    return "\n".join(translated_lines)


def main():
    pdf_path = Path('src/translation/laf.pdf')

    if not pdf_path.exists():
        print(f"❌ PDF 파일 없음: {pdf_path}")
        return

    print("=" * 70)
    print("📚 AI Publishing Platform - PDF 번역 테스트")
    print("=" * 70)
    print()

    # Step 1: PDF 추출
    print("Step 1️⃣  PDF 추출")
    print("-" * 70)
    text, metadata, pages = extract_pdf_simple(pdf_path)

    if text is None:
        print("❌ PDF 추출 실패")
        return

    print(f"✅ PDF 추출 성공")
    print(f"   총 글자: {len(text):,}")
    print(f"   총 페이지: {len(pages)}")
    print()

    # Step 2: 미리보기
    print("Step 2️⃣  추출된 텍스트 미리보기")
    print("-" * 70)
    preview = text[:500]
    print(preview)
    print("...")
    print()

    # Step 3: 청킹
    print("Step 3️⃣  텍스트 청킹 (5000글자 단위)")
    print("-" * 70)
    chunks = chunk_text(text, chunk_size=5000)
    print(f"✅ {len(chunks)}개 청크로 분할")
    for i, chunk in enumerate(chunks[:3], 1):
        print(f"   청크 {i}: {len(chunk)} 글자")
    if len(chunks) > 3:
        print(f"   ...")
    print()

    # Step 4: 번역 (모의)
    print("Step 4️⃣  번역 처리 (Mock)")
    print("-" * 70)
    print("첫 번째 청크 번역 결과:")
    translated_first = mock_translate(chunks[0][:200])
    print(translated_first)
    print()

    # Step 5: 최종 마크다운
    print("Step 5️⃣  마크다운 생성")
    print("-" * 70)
    markdown_output = f"""# {pdf_path.stem} (번역)

**원본**: English PDF
**번역**: Korean (한국어)
**페이지**: {len(pages)}
**글자 수**: {len(text):,}

## 내용

"""

    # 첫 3개 청크의 번역 추가
    for i, chunk in enumerate(chunks[:3], 1):
        markdown_output += f"### 섹션 {i}\n\n"
        translated = mock_translate(chunk[:300])
        markdown_output += translated + "\n\n"

    markdown_output += "...\n\n"
    markdown_output += f"**총 {len(chunks)}개 섹션 번역 완료**"

    # 마크다운 파일로 저장
    output_path = Path('output_laf_translated.md')
    output_path.write_text(markdown_output, encoding='utf-8')

    print(f"✅ 마크다운 파일 생성")
    print(f"   경로: {output_path.absolute()}")
    print()

    # 요약
    print("=" * 70)
    print("📊 처리 완료 요약")
    print("=" * 70)
    print(f"✅ PDF 추출: {len(pages)} 페이지")
    print(f"✅ 텍스트: {len(text):,} 글자")
    print(f"✅ 청크 분할: {len(chunks)} 개")
    print(f"✅ 번역: {len(chunks)} 청크 처리")
    print(f"✅ 마크다운: {output_path}")
    print()

    # 결과 프리뷰
    print("📝 생성된 마크다운 파일 미리보기:")
    print("-" * 70)
    print(markdown_output[:800])
    print("...")
    print()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ 오류: {e}")
        import traceback
        traceback.print_exc()
