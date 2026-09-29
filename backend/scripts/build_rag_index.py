#!/usr/bin/env python3
"""
RAG 인덱스 구축 스크립트

정제된 타로 콘텐츠를 ChromaDB에 적재
"""

import json
from pathlib import Path
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from typing import List, Dict
import argparse


class TarotRAGIndexer:
    """타로 콘텐츠 RAG 인덱싱"""

    def __init__(self, collection_name="tarot_knowledge", persist_dir="backend/rag_data/chroma_db"):
        """
        Args:
            collection_name: ChromaDB 컬렉션 이름
            persist_dir: ChromaDB 데이터 저장 경로
        """
        self.collection_name = collection_name
        self.persist_dir = Path(persist_dir)
        self.persist_dir.mkdir(parents=True, exist_ok=True)

        self.client = chromadb.PersistentClient(
            path=str(self.persist_dir),
            settings=Settings(anonymized_telemetry=False)
        )

        # 임베딩 모델 로드 (한국어 지원)
        print("📦 임베딩 모델 로딩 중...")
        self.embedding_model = SentenceTransformer('jhgan/ko-sroberta-multitask')
        print("✅ 임베딩 모델 로드 완료")

        try:
            self.collection = self.client.get_collection(name=collection_name)
            print(f"✅ 기존 컬렉션 '{collection_name}' 로드됨")
        except:
            self.collection = self.client.create_collection(
                name=collection_name,
                metadata={"description": "타로 카드 해석 및 리딩 지식 베이스"}
            )
            print(f"✅ 새로운 컬렉션 '{collection_name}' 생성됨")

    def load_refined_files(self, refined_dir: Path, min_content_length=200) -> List[Dict]:
        """정제된 JSON 파일들 로드"""

        refined_files = list(refined_dir.glob("*_refined.json"))
        print(f"📁 발견된 정제 파일: {len(refined_files)}개")

        valid_documents = []

        for file in refined_files:
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # 타로 콘텐츠가 충분히 있는 파일만 선택
                tarot_content = data.get("tarot_content", "")
                if len(tarot_content) >= min_content_length:
                    valid_documents.append({
                        "video_id": data["video_id"],
                        "content": tarot_content,
                        "summary": data.get("summary", ""),
                        "keywords": data.get("keywords", []),
                        "refined_length": data.get("refined_length", 0)
                    })
            except Exception as e:
                print(f"⚠️ 파일 로드 실패 {file.name}: {e}")
                continue

        print(f"✅ 유효한 문서: {len(valid_documents)}개 (최소 길이: {min_content_length}자)")
        return valid_documents

    def chunk_text(self, text: str, chunk_size=1000, overlap=200) -> List[str]:
        """텍스트를 청크로 분할"""

        if len(text) <= chunk_size:
            return [text]

        chunks = []
        start = 0

        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]

            # 문장 경계에서 잘리도록 조정
            if end < len(text):
                last_period = chunk.rfind('.')
                last_question = chunk.rfind('?')
                last_exclamation = chunk.rfind('!')

                split_point = max(last_period, last_question, last_exclamation)
                if split_point > chunk_size // 2:
                    chunk = chunk[:split_point + 1]
                    end = start + split_point + 1

            chunks.append(chunk.strip())
            start = end - overlap

        return chunks

    def build_index(self, documents: List[Dict], chunk_size=1000, overlap=200):
        """벡터 인덱스 구축"""

        print(f"\n🔨 벡터 인덱스 구축 중...")
        print(f"   청크 크기: {chunk_size}자, 오버랩: {overlap}자")

        all_ids = []
        all_embeddings = []
        all_texts = []
        all_metadatas = []

        for idx, doc in enumerate(documents):
            # 텍스트 청킹
            chunks = self.chunk_text(doc["content"], chunk_size, overlap)

            for chunk_idx, chunk in enumerate(chunks):
                embedding = self.embedding_model.encode(chunk, show_progress_bar=False)

                # 고유 ID 생성
                doc_id = f"{doc['video_id']}_{chunk_idx}"

                all_ids.append(doc_id)
                all_embeddings.append(embedding.tolist())
                all_texts.append(chunk)
                all_metadatas.append({
                    "video_id": doc["video_id"],
                    "chunk_index": chunk_idx,
                    "summary": doc["summary"],
                    "keywords": ",".join(doc["keywords"][:5])  # 상위 5개 키워드만
                })

            if (idx + 1) % 50 == 0:
                print(f"   진행: {idx + 1}/{len(documents)} 문서 처리됨")

        print(f"\n💾 ChromaDB에 저장 중... (총 {len(all_ids)}개 청크)")

        batch_size = 100
        for i in range(0, len(all_ids), batch_size):
            batch_end = min(i + batch_size, len(all_ids))

            self.collection.add(
                ids=all_ids[i:batch_end],
                embeddings=all_embeddings[i:batch_end],
                documents=all_texts[i:batch_end],
                metadatas=all_metadatas[i:batch_end]
            )

            print(f"   저장: {batch_end}/{len(all_ids)} 청크")

        print(f"✅ 인덱싱 완료! 총 {len(all_ids)}개 청크 저장됨")

    def get_stats(self) -> Dict:
        """컬렉션 통계"""
        count = self.collection.count()
        return {
            "collection_name": self.collection_name,
            "total_chunks": count,
            "persist_dir": str(self.persist_dir)
        }


def main():
    parser = argparse.ArgumentParser(description="RAG 인덱스 구축")
    parser.add_argument("--refined-dir", default="backend/rag_data/refined", help="정제된 파일 디렉토리")
    parser.add_argument("--persist-dir", default="backend/rag_data/chroma_db", help="ChromaDB 저장 경로")
    parser.add_argument("--collection", default="tarot_knowledge", help="컬렉션 이름")
    parser.add_argument("--chunk-size", type=int, default=1000, help="청크 크기 (characters)")
    parser.add_argument("--overlap", type=int, default=200, help="청크 오버랩 (characters)")
    parser.add_argument("--min-length", type=int, default=200, help="최소 콘텐츠 길이")
    parser.add_argument("--rebuild", action="store_true", help="기존 컬렉션 삭제 후 재구축")

    args = parser.parse_args()

    refined_dir = Path(args.refined_dir)

    if not refined_dir.exists():
        print(f"❌ 디렉토리를 찾을 수 없음: {refined_dir}")
        return

    # 기존 컬렉션 삭제 (재구축 옵션)
    if args.rebuild:
        try:
            client = chromadb.PersistentClient(
                path=args.persist_dir,
                settings=Settings(anonymized_telemetry=False)
            )
            client.delete_collection(name=args.collection)
            print(f"🗑️  기존 컬렉션 '{args.collection}' 삭제됨")
        except Exception as e:
            print(f"ℹ️  기존 컬렉션 없음: {e}")

    indexer = TarotRAGIndexer(
        collection_name=args.collection,
        persist_dir=args.persist_dir
    )

    documents = indexer.load_refined_files(refined_dir, min_content_length=args.min_length)

    if not documents:
        print("❌ 유효한 문서가 없습니다.")
        return

    indexer.build_index(
        documents=documents,
        chunk_size=args.chunk_size,
        overlap=args.overlap
    )

    stats = indexer.get_stats()
    print(f"\n📊 최종 통계:")
    print(f"   컬렉션: {stats['collection_name']}")
    print(f"   총 청크: {stats['total_chunks']}개")
    print(f"   저장 경로: {stats['persist_dir']}")

    stats_file = Path(args.persist_dir) / "index_stats.json"
    with open(stats_file, 'w', encoding='utf-8') as f:
        json.dump({
            **stats,
            "source_documents": len(documents),
            "chunk_size": args.chunk_size,
            "overlap": args.overlap,
            "min_content_length": args.min_length
        }, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 통계 저장: {stats_file}")


if __name__ == "__main__":
    main()
