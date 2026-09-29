# -*- coding: utf-8 -*-
"""
일일 통계 리포트 메일 발송. 자정에 전날 통계를 집계해서 보냄.
"""
import asyncio
import os
from datetime import datetime, timedelta, date
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from database import AsyncSessionLocal, DailyUsage, AdImpression, AdClick, TarotSession, get_kst_today
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

# 이메일 설정 (환경변수에서 로드)
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD", "")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL", "")


async def get_daily_statistics(target_date: date = None):
    """특정 날짜의 일일 통계를 집계"""
    if target_date is None:
        target_date = get_kst_today() - timedelta(days=1)

    async with AsyncSessionLocal() as db:
        # 1. 신규 방문자 수 (해당 날짜에 처음 생성된 세션)
        new_visitors_query = select(func.count(TarotSession.id)).where(
            func.date(TarotSession.created_at) == target_date
        )
        new_visitors_result = await db.execute(new_visitors_query)
        new_visitors = new_visitors_result.scalar() or 0

        # 2. 총 방문자 수 (해당 날짜에 활동한 고유 세션)
        total_visitors_query = select(func.count(func.distinct(DailyUsage.session_id))).where(
            DailyUsage.usage_date == target_date
        )
        total_visitors_result = await db.execute(total_visitors_query)
        total_visitors = total_visitors_result.scalar() or 0

        # 3. 총 타로 리딩 횟수
        total_readings_query = select(func.sum(DailyUsage.reading_count)).where(
            DailyUsage.usage_date == target_date
        )
        total_readings_result = await db.execute(total_readings_query)
        total_readings = total_readings_result.scalar() or 0

        # 4. 광고 노출 수 (총합)
        ad_impressions_query = select(func.count(AdImpression.id)).where(
            AdImpression.impression_date == target_date
        )
        ad_impressions_result = await db.execute(ad_impressions_query)
        total_ad_impressions = ad_impressions_result.scalar() or 0

        # 5. 광고 클릭 수 (총합)
        ad_clicks_query = select(func.count(AdClick.id)).where(
            AdClick.click_date == target_date
        )
        ad_clicks_result = await db.execute(ad_clicks_query)
        total_ad_clicks = ad_clicks_result.scalar() or 0

        # 6. 광고 타입별 노출/클릭 통계
        ad_type_stats = {}

        # 타입별 노출 집계
        impression_by_type_query = select(
            AdImpression.ad_type,
            func.count(AdImpression.id).label('count')
        ).where(
            AdImpression.impression_date == target_date
        ).group_by(AdImpression.ad_type)

        impression_by_type_result = await db.execute(impression_by_type_query)
        for row in impression_by_type_result:
            ad_type_stats[row.ad_type] = {
                'impressions': row.count,
                'clicks': 0
            }

        # 타입별 클릭 집계
        click_by_type_query = select(
            AdClick.ad_type,
            func.count(AdClick.id).label('count')
        ).where(
            AdClick.click_date == target_date
        ).group_by(AdClick.ad_type)

        click_by_type_result = await db.execute(click_by_type_query)
        for row in click_by_type_result:
            if row.ad_type in ad_type_stats:
                ad_type_stats[row.ad_type]['clicks'] = row.count
            else:
                ad_type_stats[row.ad_type] = {
                    'impressions': 0,
                    'clicks': row.count
                }

        # 7. CTR (Click Through Rate) 계산
        ctr = (total_ad_clicks / total_ad_impressions * 100) if total_ad_impressions > 0 else 0

        return {
            'date': target_date,
            'new_visitors': new_visitors,
            'total_visitors': total_visitors,
            'total_readings': total_readings,
            'avg_readings_per_user': round(total_readings / total_visitors, 2) if total_visitors > 0 else 0,
            'total_ad_impressions': total_ad_impressions,
            'total_ad_clicks': total_ad_clicks,
            'ctr': round(ctr, 2),
            'ad_type_stats': ad_type_stats
        }


def generate_email_html(stats: dict) -> str:
    """통계를 HTML 이메일 형식으로 변환"""

    # 광고 타입별 통계 테이블 생성
    ad_stats_rows = ""
    for ad_type, data in stats['ad_type_stats'].items():
        type_ctr = (data['clicks'] / data['impressions'] * 100) if data['impressions'] > 0 else 0
        ad_stats_rows += f"""
        <tr>
            <td style="padding: 8px; border: 1px solid #ddd;">{ad_type}</td>
            <td style="padding: 8px; border: 1px solid #ddd; text-align: right;">{data['impressions']:,}</td>
            <td style="padding: 8px; border: 1px solid #ddd; text-align: right;">{data['clicks']:,}</td>
            <td style="padding: 8px; border: 1px solid #ddd; text-align: right;">{type_ctr:.2f}%</td>
        </tr>
        """

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 800px; margin: 0 auto; padding: 20px; }}
            h1 {{ color: #6B46C1; border-bottom: 3px solid #6B46C1; padding-bottom: 10px; }}
            h2 {{ color: #553C9A; margin-top: 30px; }}
            .stats-grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; margin: 20px 0; }}
            .stat-card {{ background: #f8f9fa; border-left: 4px solid #6B46C1; padding: 15px; border-radius: 5px; }}
            .stat-label {{ color: #666; font-size: 14px; margin-bottom: 5px; }}
            .stat-value {{ font-size: 32px; font-weight: bold; color: #6B46C1; }}
            .stat-unit {{ font-size: 14px; color: #888; }}
            table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
            th {{ background-color: #6B46C1; color: white; padding: 12px; text-align: left; }}
            td {{ padding: 8px; border: 1px solid #ddd; }}
            tr:nth-child(even) {{ background-color: #f8f9fa; }}
            .footer {{ margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; color: #666; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔮 AI 타로챗 일일 리포트</h1>
            <p style="color: #666; font-size: 14px;">날짜: {stats['date'].strftime('%Y년 %m월 %d일 (%A)')}</p>

            <h2>📊 방문자 통계</h2>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-label">신규 방문자</div>
                    <div class="stat-value">{stats['new_visitors']:,} <span class="stat-unit">명</span></div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">총 방문자</div>
                    <div class="stat-value">{stats['total_visitors']:,} <span class="stat-unit">명</span></div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">타로 리딩 횟수</div>
                    <div class="stat-value">{stats['total_readings']:,} <span class="stat-unit">회</span></div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">1인당 평균 리딩</div>
                    <div class="stat-value">{stats['avg_readings_per_user']} <span class="stat-unit">회</span></div>
                </div>
            </div>

            <h2>📢 광고 통계</h2>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-label">광고 노출</div>
                    <div class="stat-value">{stats['total_ad_impressions']:,} <span class="stat-unit">회</span></div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">광고 클릭</div>
                    <div class="stat-value">{stats['total_ad_clicks']:,} <span class="stat-unit">회</span></div>
                </div>
                <div class="stat-card" style="grid-column: 1 / -1;">
                    <div class="stat-label">클릭률 (CTR)</div>
                    <div class="stat-value">{stats['ctr']}% <span class="stat-unit"></span></div>
                </div>
            </div>

            <h2>📈 광고 타입별 상세 통계</h2>
            <table>
                <thead>
                    <tr>
                        <th>광고 타입</th>
                        <th style="text-align: right;">노출 수</th>
                        <th style="text-align: right;">클릭 수</th>
                        <th style="text-align: right;">CTR</th>
                    </tr>
                </thead>
                <tbody>
                    {ad_stats_rows if ad_stats_rows else '<tr><td colspan="4" style="text-align: center; color: #999;">데이터 없음</td></tr>'}
                </tbody>
            </table>

            <div class="footer">
                <p>이 리포트는 자동으로 생성되어 발송되었습니다.</p>
                <p>문의사항: {SENDER_EMAIL}</p>
            </div>
        </div>
    </body>
    </html>
    """
    return html


def send_email(subject: str, html_content: str):
    """이메일 발송"""
    if not all([SENDER_EMAIL, SENDER_PASSWORD, RECIPIENT_EMAIL]):
        print("❌ 이메일 설정이 완료되지 않았습니다. .env 파일을 확인하세요.")
        return False

    try:
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = SENDER_EMAIL
        message["To"] = RECIPIENT_EMAIL

        html_part = MIMEText(html_content, "html", "utf-8")
        message.attach(html_part)

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, message.as_string())

        print(f"✅ 이메일 발송 완료: {RECIPIENT_EMAIL}")
        return True

    except Exception as e:
        print(f"❌ 이메일 발송 실패: {str(e)}")
        return False


async def main():
    yesterday = get_kst_today() - timedelta(days=1)
    print(f"📊 {yesterday} 통계 집계 중...")

    stats = await get_daily_statistics(yesterday)

    # 통계 출력 (디버깅용)
    print(f"\n=== 일일 통계 ({stats['date']}) ===")
    print(f"신규 방문자: {stats['new_visitors']:,}명")
    print(f"총 방문자: {stats['total_visitors']:,}명")
    print(f"타로 리딩: {stats['total_readings']:,}회")
    print(f"1인당 평균: {stats['avg_readings_per_user']}회")
    print(f"광고 노출: {stats['total_ad_impressions']:,}회")
    print(f"광고 클릭: {stats['total_ad_clicks']:,}회")
    print(f"CTR: {stats['ctr']}%")
    print()

    html_content = generate_email_html(stats)

    subject = f"🔮 AI 타로챗 일일 리포트 - {stats['date'].strftime('%Y.%m.%d')}"
    send_email(subject, html_content)


if __name__ == "__main__":
    asyncio.run(main())
