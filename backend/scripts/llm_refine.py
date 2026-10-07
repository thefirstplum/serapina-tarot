#!/usr/bin/env python3
"""
LLM 기반 타로 콘텐츠 정제 스크립트

1단계 전처리된 텍스트를 LLM으로 추가 정제:
- 타로 해석 내용만 추출
- 광고/인사말 제거
- 핵심 타로 리딩 내용 요약
"""

import json
import httpx
from pathlib import Path
import argparse
from typing import List, Dict


class TarotContentRefiner:
    """LLM 기반 타로 콘텐츠 정제"""

    def __init__(self, ollama_url="http://localhost:11434", model="gpt-oss:20b"):
        self.ollama_url = ollama_url
        self.model = model

    def extract_tarot_readings(self, text: str) -> Dict:
        """전체 텍스트에서 타로 해석 부분만 추출"""

        prompt = f"""다음은 타로 유튜브 영상의 자막입니다. 타로 카드 해석과 관련된 핵심 내용만 간단히 추출해주세요.

**제외할 내용:**
인사말, 구독요청, 광고, 일상대화

**포함할 내용:**
타로 카드 해석 방법, 카드 의미 설명, 리딩 예시, 상담 기법

**자막:**
{text[:8000]}

**형식:**
타로 핵심 내용: (여기에 요약)
주요 주제: (1문장)
키워드: 키워드1, 키워드2, 키워드3
"""

        try:
            print(f"🤖 LLM 정제 중... (텍스트 길이: {len(text)} chars)")

            with httpx.Client(timeout=180.0) as client:
                response = client.post(
                    f"{self.ollama_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False
                    }
                )

                if response.status_code == 200:
                    result = response.json()
                    raw_response = result.get("response", "")

                    # 응답 파싱
                    content = {"tarot_content": "", "summary": "", "keywords": []}

                    lines = raw_response.strip().split('\n')
                    for line in lines:
                        if line.startswith('타로 핵심 내용:'):
                            content["tarot_content"] = line.replace('타로 핵심 내용:', '').strip()
                        elif line.startswith('주요 주제:'):
                            content["summary"] = line.replace('주요 주제:', '').strip()
                        elif line.startswith('키워드:'):
                            keywords = line.replace('키워드:', '').strip()
                            content["keywords"] = [k.strip() for k in keywords.split(',')]

                    # 파싱 실패 시 전체 응답 사용
                    if not content["tarot_content"]:
                        content["tarot_content"] = raw_response[:1000]
                        content["summary"] = "자동 추출 실패"
                        content["keywords"] = ["타로", "리딩"]

                    print(f"✅ LLM 정제 완료")
                    print(f"   요약: {content.get('summary', 'N/A')}")
                    print(f"   키워드: {', '.join(content.get('keywords', []))}")

                    return content
                else:
                    print(f"❌ LLM 응답 오류: {response.status_code}")
                    return {"error": "API error", "tarot_content": text[:1000], "summary": "오류", "keywords": []}

        except Exception as e:
            print(f"❌ LLM 정제 오류: {e}")
            return {"error": str(e), "tarot_content": text[:1000], "summary": "오류", "keywords": []}

    def split_and_refine(self, text: str, chunk_size=10000) -> List[Dict]:
        """긴 텍스트를 나눠서 정제"""

        chunks = []
        words = text.split()

        current_chunk = []
        current_length = 0

        for word in words:
            current_chunk.append(word)
            current_length += len(word) + 1

            if current_length >= chunk_size:
                chunks.append(' '.join(current_chunk))
                current_chunk = []
                current_length = 0

        if current_chunk:
            chunks.append(' '.join(current_chunk))

        print(f"📑 텍스트를 {len(chunks)}개 청크로 분할")

        results = []
        for i, chunk in enumerate(chunks, 1):
            print(f"\n[청크 {i}/{len(chunks)}]")
            result = self.extract_tarot_readings(chunk)
            if not result.get("error"):
                results.append(result)

        return results

    def merge_results(self, results: List[Dict]) -> Dict:
        """여러 청크의 결과를 병합"""

        all_content = []
        all_keywords = set()
        summaries = []

        for result in results:
            if result.get("tarot_content"):
                all_content.append(result["tarot_content"])
            if result.get("keywords"):
                all_keywords.update(result["keywords"])
            if result.get("summary"):
                summaries.append(result["summary"])

        merged = {
            "tarot_content": "\n\n".join(all_content),
            "summary": " / ".join(summaries),
            "keywords": list(all_keywords),
            "chunk_count": len(results)
        }

        return merged


def main():
    parser = argparse.ArgumentParser(description="LLM 기반 타로 콘텐츠 정제")
    parser.add_argument("--input-dir", default="backend/rag_data/processed", help="전처리된 파일 경로")
    parser.add_argument("--output-dir", default="backend/rag_data/refined", help="정제된 결과 저장 경로")
    parser.add_argument("--video-id", help="특정 비디오만 처리")
    parser.add_argument("--chunk-size", type=int, default=10000, help="청크 크기 (characters)")

    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    refiner = TarotContentRefiner()

    if args.video_id:
        processed_files = list(input_dir.glob(f"{args.video_id}_processed.json"))
    else:
        processed_files = list(input_dir.glob("*_processed.json"))

    print(f"📁 발견된 파일: {len(processed_files)}개\n")

    all_refined = []

    for processed_file in processed_files:
        print(f"\n{'='*60}")
        print(f"📄 처리 중: {processed_file.name}")

        with open(processed_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        video_id = data["video_id"]
        cleaned_text = data["cleaned_text"]

        # 텍스트가 너무 길면 분할 처리
        if len(cleaned_text) > args.chunk_size:
            results = refiner.split_and_refine(cleaned_text, args.chunk_size)
            refined = refiner.merge_results(results)
        else:
            refined = refiner.extract_tarot_readings(cleaned_text)

        output_data = {
            "video_id": video_id,
            "original_length": data["original_length"],
            "cleaned_length": len(cleaned_text),
            "refined_length": len(refined.get("tarot_content", "")),
            "summary": refined.get("summary"),
            "keywords": refined.get("keywords", []),
            "tarot_content": refined.get("tarot_content"),
            "chunk_count": refined.get("chunk_count", 1)
        }

        output_file = output_dir / f"{video_id}_refined.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)

        print(f"\n💾 저장: {output_file.name}")
        print(f"   원본: {data['original_length']} chars")
        print(f"   정제1: {len(cleaned_text)} chars")
        print(f"   정제2: {len(refined.get('tarot_content', ''))} chars")

        all_refined.append(output_data)

    summary_file = output_dir / "refine_summary.json"
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump({
            "total_files": len(all_refined),
            "total_keywords": len(set(kw for r in all_refined for kw in r.get("keywords", []))),
            "files": all_refined
        }, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 정제 완료!")
    print(f"📊 총 {len(all_refined)}개 파일 처리됨")


if __name__ == "__main__":
    main()
