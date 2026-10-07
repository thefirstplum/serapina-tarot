#!/bin/bash
# 타로 자막 자동 수집 및 처리 스크립트 (백그라운드 실행용)

LOG_FILE="backend/rag_data/auto_collect.log"
SCRIPT_DIR="backend/scripts"
SLEEP_TIME=5  # 다운로드 간 대기 시간 (초)

# 인기 타로 운세 키워드 (실제 해석 사례 중심)
KEYWORDS=(
    "타로 운세"
    "타로 큰복"
    "타로 정확"
    "타로 소름"
    "타로 대박"
    "타로 속마음"
    "타로 그사람"
    "타로 연애운"
    "타로 결혼운"
    "타로 사랑"
    "타로 재회"
    "타로 짝사랑"
    "타로 생각"
    "타로 진심"
    "타로 감정"
    "타로 관계"
    "타로 인연"
    "타로 미래"
    "타로 행운"
    "타로 경사"
    "타로 예언"
    "타로 직진"
    "타로 팩폭"
    "타로 작두"
    "타로 축하"
    "타로 응원"
    "타로 귀인"
    "타로 비밀"
    "타로 욕망"
    "타로 고민"
    "타로 해결"
    "타로 만남"
    "타로 사건"
    "타로 우정"
    "타로 주간운세"
    "타로 오늘운세"
    "타로 가을"
    "타로 겨울"
    "타로 봄"
    "타로 여름"
)

echo "========================================" | tee -a "$LOG_FILE"
echo "타로 자막 자동 수집 시작" | tee -a "$LOG_FILE"
echo "시작 시간: $(date)" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"

# 1단계: 다양한 키워드로 자막 다운로드
for keyword in "${KEYWORDS[@]}"; do
    echo "" | tee -a "$LOG_FILE"
    echo "[다운로드] 검색어: $keyword" | tee -a "$LOG_FILE"

    python3 "$SCRIPT_DIR/download_tarot_subtitles.py" \
        --search "$keyword" \
        --max-results 50 \
        2>&1 | tee -a "$LOG_FILE"

    # 다운로드 간 대기 (서버 부하 방지)
    echo "대기 중... (${SLEEP_TIME}초)" | tee -a "$LOG_FILE"
    sleep $SLEEP_TIME
done

# 현재 다운로드된 파일 수 확인
SUBTITLE_COUNT=$(ls -1 backend/rag_data/subtitles/*.vtt 2>/dev/null | wc -l)
echo "" | tee -a "$LOG_FILE"
echo "총 다운로드된 자막: ${SUBTITLE_COUNT}개" | tee -a "$LOG_FILE"

# 2단계: 전체 전처리 (새로운 파일만)
echo "" | tee -a "$LOG_FILE"
echo "[전처리] 1차 정제 시작..." | tee -a "$LOG_FILE"

python3 "$SCRIPT_DIR/preprocess_subtitles.py" 2>&1 | tee -a "$LOG_FILE"

PROCESSED_COUNT=$(ls -1 backend/rag_data/processed/*_processed.json 2>/dev/null | wc -l)
echo "전처리 완료: ${PROCESSED_COUNT}개" | tee -a "$LOG_FILE"

# 3단계: LLM 정제 (새로운 파일만)
echo "" | tee -a "$LOG_FILE"
echo "[정제] 2차 LLM 정제 시작..." | tee -a "$LOG_FILE"

python3 "$SCRIPT_DIR/llm_refine.py" --chunk-size 8000 2>&1 | tee -a "$LOG_FILE"

REFINED_COUNT=$(ls -1 backend/rag_data/refined/*_refined.json 2>/dev/null | wc -l)
echo "LLM 정제 완료: ${REFINED_COUNT}개" | tee -a "$LOG_FILE"

# 완료
echo "" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"
echo "자동 수집 완료!" | tee -a "$LOG_FILE"
echo "종료 시간: $(date)" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"
echo "📊 최종 결과:" | tee -a "$LOG_FILE"
echo "  - 자막 파일: ${SUBTITLE_COUNT}개" | tee -a "$LOG_FILE"
echo "  - 전처리 파일: ${PROCESSED_COUNT}개" | tee -a "$LOG_FILE"
echo "  - LLM 정제 파일: ${REFINED_COUNT}개" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# 요약 파일 생성
cat > backend/rag_data/collection_summary.txt <<EOF
타로 RAG 데이터 수집 요약
========================

수집 완료 시간: $(date)

파일 통계:
- 자막 파일 (.vtt): ${SUBTITLE_COUNT}개
- 전처리 파일 (.json): ${PROCESSED_COUNT}개
- LLM 정제 파일 (.json): ${REFINED_COUNT}개

검색 키워드 (${#KEYWORDS[@]}개):
$(printf '%s\n' "${KEYWORDS[@]}" | sed 's/^/  - /')

로그 파일: ${LOG_FILE}
EOF

echo "✅ 요약 파일 생성: backend/rag_data/collection_summary.txt" | tee -a "$LOG_FILE"
cat backend/rag_data/collection_summary.txt | tee -a "$LOG_FILE"
