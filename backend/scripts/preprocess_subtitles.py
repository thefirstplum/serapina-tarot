#!/usr/bin/env python3
"""
자막 전처리 스크립트

1단계: 규칙 기반으로 VTT를 텍스트로 정제
2단계: LLM으로 타로 해석 문장만 추출 (--use-llm)
"""

import re
import json
from pathlib import Path
from typing import List, Dict
import argparse


class SubtitlePreprocessor:
    """1단계: 규칙 기반 자막 정제"""

    def __init__(self):
        # 제거할 패턴들
        self.noise_patterns = [
            r'<[^>]+>',  # HTML 태그
            r'\d{2}:\d{2}:\d{2}\.\d{3}',  # 타임스탬프
            r'-->',
            r'WEBVTT',
            r'Kind: captions',
            r'Language: \w+',
            r'align:\w+',
            r'position:\d+%',
        ]

        # 필터링할 불필요한 문구들
        self.filter_phrases = [
            r'^안녕하세요',
            r'구독',
            r'좋아요',
            r'알림',
            r'댓글',
            r'링크는 설명란',
            r'오늘도 시청해',
            r'감사합니다',
        ]

    def clean_vtt(self, vtt_content: str) -> str:
        """VTT 파일을 순수 텍스트로 변환"""
        lines = vtt_content.split('\n')
        cleaned_lines = []

        for line in lines:
            line = line.strip()

            # 빈 줄 스킵
            if not line:
                continue

            # 타임스탬프 라인 스킵
            if '-->' in line:
                continue

            # WEBVTT 헤더 스킵
            if line.startswith('WEBVTT') or line.startswith('Kind:') or line.startswith('Language:'):
                continue

            # 숫자만 있는 라인 스킵 (자막 번호)
            if line.isdigit():
                continue

            for pattern in self.noise_patterns:
                line = re.sub(pattern, '', line)

            line = line.strip()

            if line and len(line) > 1:
                cleaned_lines.append(line)

        # 중복 제거 (연속된 같은 문장)
        deduplicated = []
        prev_line = None
        for line in cleaned_lines:
            if line != prev_line:
                deduplicated.append(line)
                prev_line = line

        return '\n'.join(deduplicated)

    def split_sentences(self, text: str) -> List[str]:
        """텍스트를 문장 단위로 분리"""
        # 한국어 문장 구분
        sentences = re.split(r'[.!?]\s+|\n', text)
        sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 10]
        return sentences

    def filter_noise(self, sentences: List[str]) -> List[str]:
        """불필요한 문장 필터링"""
        filtered = []

        for sentence in sentences:
            # 너무 짧은 문장 제외
            if len(sentence) < 10:
                continue

            # 필터 패턴 체크
            is_noise = False
            for pattern in self.filter_phrases:
                if re.search(pattern, sentence):
                    is_noise = True
                    break

            if not is_noise:
                filtered.append(sentence)

        return filtered

    def preprocess_file(self, vtt_file: Path) -> Dict:
        """VTT 파일 전처리"""
        print(f"📄 전처리 중: {vtt_file.name}")

        with open(vtt_file, 'r', encoding='utf-8') as f:
            vtt_content = f.read()

        cleaned_text = self.clean_vtt(vtt_content)

        sentences = self.split_sentences(cleaned_text)

        filtered_sentences = self.filter_noise(sentences)

        print(f"  원본: {len(vtt_content)} chars")
        print(f"  정제: {len(cleaned_text)} chars")
        print(f"  문장: {len(sentences)} → {len(filtered_sentences)} (필터 후)")

        return {
            "video_id": vtt_file.stem.replace('.ko', ''),
            "original_length": len(vtt_content),
            "cleaned_text": cleaned_text,
            "sentences": filtered_sentences,
            "sentence_count": len(filtered_sentences)
        }


class LLMContentClassifier:
    """2단계: LLM 기반 타로 해석 추출"""

    def __init__(self, ollama_url="http://localhost:11434", model="gpt-oss:20b"):
        self.ollama_url = ollama_url
        self.model = model

    def classify_content(self, text: str) -> Dict:
        """텍스트가 타로 해석인지 분류"""
        import httpx

        prompt = f"""다음 텍스트를 분석해서 분류해주세요.

텍스트: "{text}"

분류 기준:
1. tarot_reading: 타로 카드 해석, 운세, 리딩 내용
2. intro: 인사말, 소개, 채널 안내
3. outro: 마무리 인사, 구독 요청
4. advertisement: 광고, 프로모션
5. noise: 기타 불필요한 내용

JSON 형식으로 답변:
{{"category": "tarot_reading|intro|outro|advertisement|noise", "confidence": 0.0-1.0}}
"""

        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.post(
                    f"{self.ollama_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "format": "json"
                    }
                )

                if response.status_code == 200:
                    result = response.json()
                    classification = json.loads(result.get("response", "{}"))
                    return classification
                else:
                    return {"category": "unknown", "confidence": 0.0}

        except Exception as e:
            print(f"  ⚠️  LLM 분류 오류: {e}")
            return {"category": "unknown", "confidence": 0.0}

    def extract_tarot_content(self, sentences: List[str], batch_size=5) -> List[Dict]:
        """타로 해석 문장만 추출"""
        print(f"\n🤖 LLM 분류 시작 ({len(sentences)}개 문장)")

        tarot_sentences = []

        # 문장을 배치로 묶어서 처리 (속도 향상)
        for i in range(0, len(sentences), batch_size):
            batch = sentences[i:i+batch_size]
            batch_text = ' '.join(batch)

            print(f"  [{i+1}-{min(i+batch_size, len(sentences))}/{len(sentences)}] 분류 중...")
            classification = self.classify_content(batch_text)

            if classification.get("category") == "tarot_reading":
                for sentence in batch:
                    tarot_sentences.append({
                        "text": sentence,
                        "confidence": classification.get("confidence", 0.0)
                    })

        print(f"✅ 타로 해석 추출: {len(tarot_sentences)}개")
        return tarot_sentences


def main():
    parser = argparse.ArgumentParser(description="자막 전처리")
    parser.add_argument("--input-dir", default="backend/rag_data/subtitles", help="자막 파일 경로")
    parser.add_argument("--output-dir", default="backend/rag_data/processed", help="출력 경로")
    parser.add_argument("--use-llm", action="store_true", help="LLM 분류 사용")
    parser.add_argument("--video-id", help="특정 비디오만 처리")

    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1단계: 규칙 기반 전처리
    preprocessor = SubtitlePreprocessor()

    if args.video_id:
        vtt_files = list(input_dir.glob(f"{args.video_id}*.vtt"))
    else:
        vtt_files = list(input_dir.glob("*.vtt"))

    print(f"📁 발견된 자막 파일: {len(vtt_files)}개\n")

    all_results = []

    for vtt_file in vtt_files:
        result = preprocessor.preprocess_file(vtt_file)

        # 2단계: LLM 분류 (옵션)
        if args.use_llm:
            classifier = LLMContentClassifier()
            tarot_content = classifier.extract_tarot_content(result["sentences"])
            result["tarot_content"] = tarot_content
            result["tarot_sentence_count"] = len(tarot_content)

        all_results.append(result)

        output_file = output_dir / f"{result['video_id']}_processed.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        print(f"💾 저장: {output_file.name}\n")

    summary_file = output_dir / "preprocessing_summary.json"
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump({
            "total_files": len(all_results),
            "total_sentences": sum(r["sentence_count"] for r in all_results),
            "files": all_results
        }, f, ensure_ascii=False, indent=2)

    print(f"✅ 전처리 완료!")
    print(f"📊 총 {len(all_results)}개 파일, {sum(r['sentence_count'] for r in all_results)}개 문장")


if __name__ == "__main__":
    main()
