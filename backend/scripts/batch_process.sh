#!/bin/bash
# 타로 RAG 데이터 대량 처리 스크립트

LOG_FILE="backend/rag_data/batch_process.log"
SCRIPT_DIR="backend/scripts"

echo "========================================" | tee -a "$LOG_FILE"
echo "타로 RAG 데이터 배치 처리 시작" | tee -a "$LOG_FILE"
echo "시작 시간: $(date)" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"

# 1단계: 자막 다운로드 (여러 검색어)
echo "" | tee -a "$LOG_FILE"
echo "[1/3] 자막 다운로드 중..." | tee -a "$LOG_FILE"

python3 "$SCRIPT_DIR/download_tarot_subtitles.py" --search "타로 리딩" --max-results 30 2>&1 | tee -a "$LOG_FILE"
python3 "$SCRIPT_DIR/download_tarot_subtitles.py" --search "타로 연애운" --max-results 30 2>&1 | tee -a "$LOG_FILE"
python3 "$SCRIPT_DIR/download_tarot_subtitles.py" --search "타로 취업운" --max-results 30 2>&1 | tee -a "$LOG_FILE"
python3 "$SCRIPT_DIR/download_tarot_subtitles.py" --search "타로 금전운" --max-results 30 2>&1 | tee -a "$LOG_FILE"
python3 "$SCRIPT_DIR/download_tarot_subtitles.py" --search "타로카드 해석" --max-results 30 2>&1 | tee -a "$LOG_FILE"

# 다운로드 결과 확인
SUBTITLE_COUNT=$(ls -1 backend/rag_data/subtitles/*.vtt 2>/dev/null | wc -l)
echo "다운로드된 자막 파일: ${SUBTITLE_COUNT}개" | tee -a "$LOG_FILE"

# 2단계: 1차 전처리 (규칙 기반)
echo "" | tee -a "$LOG_FILE"
echo "[2/3] 1차 전처리 중 (규칙 기반)..." | tee -a "$LOG_FILE"

python3 "$SCRIPT_DIR/preprocess_subtitles.py" 2>&1 | tee -a "$LOG_FILE"

# 전처리 결과 확인
PROCESSED_COUNT=$(ls -1 backend/rag_data/processed/*_processed.json 2>/dev/null | wc -l)
echo "전처리된 파일: ${PROCESSED_COUNT}개" | tee -a "$LOG_FILE"

# 3단계: 2차 정제 (LLM 기반)
echo "" | tee -a "$LOG_FILE"
echo "[3/3] 2차 정제 중 (LLM)..." | tee -a "$LOG_FILE"

python3 "$SCRIPT_DIR/llm_refine.py" --chunk-size 8000 2>&1 | tee -a "$LOG_FILE"

# 정제 결과 확인
REFINED_COUNT=$(ls -1 backend/rag_data/refined/*_refined.json 2>/dev/null | wc -l)
echo "정제된 파일: ${REFINED_COUNT}개" | tee -a "$LOG_FILE"

# 완료
echo "" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"
echo "배치 처리 완료!" | tee -a "$LOG_FILE"
echo "종료 시간: $(date)" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"
echo "📊 최종 결과:" | tee -a "$LOG_FILE"
echo "  - 자막 다운로드: ${SUBTITLE_COUNT}개" | tee -a "$LOG_FILE"
echo "  - 1차 전처리: ${PROCESSED_COUNT}개" | tee -a "$LOG_FILE"
echo "  - 2차 LLM 정제: ${REFINED_COUNT}개" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"
echo "✅ 로그 파일: $LOG_FILE" | tee -a "$LOG_FILE"
