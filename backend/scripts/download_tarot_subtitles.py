#!/usr/bin/env python3
"""
유튜브 타로 영상 자막 다운로드 스크립트

사용법:
  python download_tarot_subtitles.py --search "타로 리딩" --max-results 50
  python download_tarot_subtitles.py --video-id "9Rw931ByMbA"
"""

import argparse
import json
import os
import subprocess
from pathlib import Path
from datetime import datetime


class TarotSubtitleDownloader:
    def __init__(self, output_dir="backend/rag_data/subtitles"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_file = self.output_dir / "metadata.json"
        self.metadata = self._load_metadata()

    def _load_metadata(self):
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"videos": []}

    def _save_metadata(self):
        with open(self.metadata_file, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, ensure_ascii=False, indent=2)

    def search_videos(self, query, max_results=50):
        """유튜브에서 타로 영상 검색"""
        print(f"🔍 검색 중: '{query}' (최대 {max_results}개)")

        cmd = [
            "yt-dlp",
            f"ytsearch{max_results}:{query}",
            "--get-id",
            "--get-title",
            "--get-duration",
            "--get-description",
            "--skip-download"
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
            lines = result.stdout.strip().split('\n')

            # 결과를 4줄씩 묶어서 파싱 (제목, ID, 길이, 설명)
            videos = []
            for i in range(0, len(lines), 4):
                if i + 1 < len(lines):
                    videos.append({
                        "title": lines[i],
                        "video_id": lines[i + 1],
                        "duration": lines[i + 2] if i + 2 < len(lines) else "",
                        "description": lines[i + 3] if i + 3 < len(lines) else ""
                    })

            print(f"✅ {len(videos)}개 영상 발견")
            return videos

        except subprocess.TimeoutExpired:
            print("⚠️  검색 타임아웃")
            return []
        except Exception as e:
            print(f"❌ 검색 오류: {e}")
            return []

    def download_subtitle(self, video_id, title=""):
        """단일 영상의 자막 다운로드"""
        print(f"📥 자막 다운로드 중: {title or video_id}")

        # 이미 다운로드한 영상인지 확인
        existing = next((v for v in self.metadata["videos"] if v["video_id"] == video_id), None)
        if existing and existing.get("subtitle_downloaded"):
            print(f"⏭️  이미 다운로드됨: {video_id}")
            return True

        output_path = self.output_dir / f"{video_id}"

        cmd = [
            "yt-dlp",
            f"https://www.youtube.com/watch?v={video_id}",
            "--write-auto-sub",  # 자동 생성 자막
            "--write-sub",       # 수동 자막
            "--sub-lang", "ko",  # 한국어 자막
            "--skip-download",   # 비디오는 다운 안 함
            "--output", str(output_path)
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

            # 자막 파일 확인
            subtitle_files = list(self.output_dir.glob(f"{video_id}*.vtt")) + \
                           list(self.output_dir.glob(f"{video_id}*.srt"))

            if subtitle_files:
                print(f"✅ 자막 다운로드 완료: {subtitle_files[0].name}")

                # 메타데이터 업데이트
                video_info = {
                    "video_id": video_id,
                    "title": title,
                    "subtitle_file": subtitle_files[0].name,
                    "subtitle_downloaded": True,
                    "downloaded_at": datetime.now().isoformat()
                }

                if existing:
                    self.metadata["videos"].remove(existing)
                self.metadata["videos"].append(video_info)
                self._save_metadata()

                return True
            else:
                print(f"⚠️  자막 없음: {video_id}")

                # 자막 없음을 메타데이터에 기록
                video_info = {
                    "video_id": video_id,
                    "title": title,
                    "subtitle_downloaded": False,
                    "no_subtitle": True,
                    "checked_at": datetime.now().isoformat()
                }

                if existing:
                    self.metadata["videos"].remove(existing)
                self.metadata["videos"].append(video_info)
                self._save_metadata()

                return False

        except subprocess.TimeoutExpired:
            print(f"⚠️  다운로드 타임아웃: {video_id}")
            return False
        except Exception as e:
            print(f"❌ 다운로드 오류: {e}")
            return False

    def download_from_search(self, query, max_results=50):
        """검색 결과의 자막 일괄 다운로드"""
        videos = self.search_videos(query, max_results)

        success_count = 0
        fail_count = 0

        for i, video in enumerate(videos, 1):
            print(f"\n[{i}/{len(videos)}]")
            if self.download_subtitle(video["video_id"], video["title"]):
                success_count += 1
            else:
                fail_count += 1

        print(f"\n📊 완료: 성공 {success_count}개, 실패 {fail_count}개")
        return success_count, fail_count


def main():
    parser = argparse.ArgumentParser(description="유튜브 타로 영상 자막 다운로드")
    parser.add_argument("--search", help="검색 키워드")
    parser.add_argument("--video-id", help="특정 영상 ID")
    parser.add_argument("--max-results", type=int, default=50, help="최대 검색 결과 수")
    parser.add_argument("--output-dir", default="backend/rag_data/subtitles", help="저장 경로")

    args = parser.parse_args()

    downloader = TarotSubtitleDownloader(args.output_dir)

    if args.video_id:
        downloader.download_subtitle(args.video_id)
    elif args.search:
        downloader.download_from_search(args.search, args.max_results)
    else:
        # 기본 검색어들
        queries = [
            "타로 리딩",
            "타로 연애운",
            "타로 취업운",
            "타로 금전운",
            "타로 건강운",
            "타로카드 해석"
        ]

        for query in queries:
            print(f"\n{'='*60}")
            downloader.download_from_search(query, max_results=20)


if __name__ == "__main__":
    main()
