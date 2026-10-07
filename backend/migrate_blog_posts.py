# -*- coding: utf-8 -*-
"""
블로그 포스트 데이터를 MySQL DB로 마이그레이션하는 스크립트
"""
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import AsyncSessionLocal, BlogPost, create_tables
from datetime import datetime

# 기존 블로그 포스트 데이터
BLOG_POSTS_DATA = [
    {
        "title": "같은 반 남학생 짝사랑 3개월째, 고백해도 될까?",
        "category": "연애",
        "excerpt": "매일 보는 같은 반 남학생이 너무 좋은데 고백하기가 무서워요. 타로가 알려주는 연애운은?",
        "situation": "고등학교 2학년 여학생입니다. 같은 반에 있는 남학생을 3개월째 짝사랑하고 있어요. 매일 보는데도 말 한번 제대로 못 걸어봤어요. 친구들은 고백하라고 하는데 거절당하면 어떡하죠? 남은 1년 동안 학교 다니기 진짜 힘들 것 같아요. 그냥 마음속에만 담아둘까요, 아니면 용기내서 고백할까요?",
        "cards": [
            {"id": "cups02", "name": "컵 2", "position": "정방향"},
            {"id": "swords02", "name": "검 2", "position": "정방향"},
            {"id": "maj06", "name": "연인", "position": "정방향"}
        ],
        "interpretations": [
            "<strong>과거 - 컵 2 (정방향):</strong> 너의 마음속에는 이미 그 남학생과의 아름다운 연결이 자리잡고 있어. 3개월 동안 품어온 감정은 진실하고 순수한 마음에서 비롯된 거야. 이건 단순한 호기심이 아니라 진짜 감정이라는 뜻이지.",
            "<strong>현재 - 검 2 (정방향):</strong> 지금 너는 선택의 기로에 서 있어. 고백할까 말까, 이 결정을 내리기가 정말 어렵지? 머리로는 이것저것 걱정되지만, 마음 한편으로는 용기를 내고 싶은 게 느껴져. 이 갈등 자체가 네가 성장하고 있다는 증거야.",
            "<strong>미래 - 연인 (정방향):</strong> 와, 이건 정말 좋은 카드야! 용기를 내서 진심을 전한다면 아름다운 관계가 시작될 수 있어. 설령 연애로 발전하지 않더라도, 솔직한 마음을 나누는 것 자체가 너희 둘 사이에 특별한 인연을 만들어줄 거야."
        ],
        "advice": "타로는 네가 용기를 내라고 말하고 있어. 물론 무섭지. 거절당할 수도 있고, 어색해질 수도 있어. 하지만 3개월 동안 품어온 마음을 계속 숨기는 것도 힘든 일이잖아?<br><br>고백은 결과보다 과정이 중요해. 네 진심을 전하는 것 자체가 용기있는 행동이야. 그리고 타로가 보여주는 미래는 긍정적이야. 설령 지금 당장은 아니더라도, 솔직한 마음을 나눈 것이 나중에 좋은 결과를 가져올 거야.<br><br><strong>팁:</strong> 갑자기 고백하기 부담스럽다면, 먼저 친해지는 시간을 가져봐. 작은 대화부터 시작해서 서로를 알아가는 거야. 그 과정에서 자연스럽게 마음을 전할 수 있을 거야! 💕",
        "tags": ["짝사랑", "고백", "학교", "연애운", "고등학생"],
        "gradient": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
        "emoji": "💕",
        "published_at": "2025-10-12"
    },
    # 나머지 11개 포스트도 여기 추가...
]

async def migrate_posts():
    """블로그 포스트를 DB에 마이그레이션"""
    print("🔄 Creating database tables...")
    await create_tables()

    print("🔄 Starting migration...")

    async with AsyncSessionLocal() as session:
        try:
            # 기존 포스트를 전부 지우고 다시 넣음. 개발 환경에서만 실행
            from sqlalchemy import delete
            await session.execute(delete(BlogPost))
            await session.commit()
            print("✅ Cleared existing posts")

            for i, post_data in enumerate(BLOG_POSTS_DATA, 1):
                post = BlogPost(
                    title=post_data["title"],
                    category=post_data["category"],
                    excerpt=post_data["excerpt"],
                    situation=post_data["situation"],
                    cards=post_data["cards"],
                    interpretations=post_data["interpretations"],
                    advice=post_data["advice"],
                    tags=post_data["tags"],
                    gradient=post_data["gradient"],
                    emoji=post_data["emoji"],
                    published=True,
                    view_count=0,
                    published_at=datetime.strptime(post_data["published_at"], "%Y-%m-%d")
                )
                session.add(post)
                print(f"✅ Added post {i}: {post_data['title']}")

            await session.commit()
            print(f"\n🎉 Successfully migrated {len(BLOG_POSTS_DATA)} blog posts!")

        except Exception as e:
            print(f"❌ Error during migration: {e}")
            await session.rollback()
            raise

if __name__ == "__main__":
    asyncio.run(migrate_posts())
