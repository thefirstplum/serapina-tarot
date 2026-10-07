<template>
  <div class="app-main">
      <div class="page-layout">
        <!-- Header -->
        <div class="page-header">
          <div class="header-content">
            <v-btn
              to="/"
              icon
              variant="text"
              class="back-button"
            >
              <v-icon color="white">mdi-arrow-left</v-icon>
            </v-btn>
            <div class="header-text">
              <h1 class="page-title">{{ t('legal.privacy.title') }}</h1>
              <p class="page-subtitle">{{ t('legal.privacy.subtitle') }}</p>
            </div>
          </div>
        </div>

        <!-- Content -->
        <div class="page-content">
          <div class="content-container">
            <section class="info-card">
              <h2 class="section-title">제1조 (개인정보의 수집 및 이용 목적)</h2>
              <p class="section-text">
                세라피나 타로(이하 "서비스")는 다음의 목적을 위하여 개인정보를 처리합니다.
                처리된 개인정보는 다음의 목적 이외의 용도로는 이용되지 않으며, 이용 목적이 변경되는 경우에는 관련 법령에 따라 별도의 동의를 받는 등 필요한 조치를 이행할 예정입니다.
              </p>
              <ul class="section-list">
                <li>타로 리딩 서비스 제공 및 상담 내용 기록</li>
                <li>서비스 개선을 위한 통계 분석 및 품질 향상</li>
                <li>고객 문의 및 불만 처리를 위한 의사소통 경로 확보</li>
              </ul>
            </section>

            <section class="info-card">
              <h2 class="section-title">제2조 (수집하는 개인정보의 항목)</h2>
              <p class="section-text">
                서비스는 서비스 제공을 위해 다음과 같은 정보를 자동으로 수집합니다.
              </p>
              <ul class="section-list">
                <li>서비스 이용 기록: 세션 ID, 접속 로그, 이용 시간</li>
                <li>기기 정보: 브라우저 종류 및 버전, 운영체제</li>
                <li>서비스 이용 내용: 질문 내용, 선택한 타로 카드, AI 해석 결과 (AES-256 암호화 저장)</li>
              </ul>
              <div class="alert-box">
                <strong>중요 안내:</strong> 본 서비스는 회원가입이 필요하지 않으며, 이름, 연락처, 주민등록번호 등의 개인 식별 정보를 수집하지 않습니다.
                민감한 개인정보(주민등록번호, 계좌번호, 비밀번호 등)는 절대 입력하지 마십시오.
              </div>
            </section>

            <section class="info-card">
              <h2 class="section-title">제3조 (개인정보의 보유 및 이용 기간)</h2>
              <p class="section-text">
                서비스는 이용자의 개인정보를 수집 목적 달성 시까지 보유 및 이용합니다.
              </p>
              <ul class="section-list">
                <li>세션 데이터: 서비스 이용 기간 동안 보관</li>
                <li>상담 기록: 서비스 품질 개선 및 통계 분석을 위해 보관</li>
                <li>이용자가 삭제를 요청하는 경우 지체 없이 파기합니다</li>
              </ul>
            </section>

            <section class="info-card">
              <h2 class="section-title">제4조 (개인정보의 파기 절차 및 방법)</h2>
              <ul class="section-list">
                <li>파기 절차: 이용자의 개인정보는 목적 달성 후 내부 방침에 따라 일정 기간 저장된 후 파기됩니다</li>
                <li>파기 방법: 전자적 파일 형태의 정보는 기록을 재생할 수 없는 기술적 방법을 사용하여 삭제합니다</li>
              </ul>
            </section>

            <section class="info-card">
              <h2 class="section-title">제5조 (개인정보의 안전성 확보 조치)</h2>
              <p class="section-text">
                서비스는 개인정보의 안전성 확보를 위해 다음과 같은 조치를 취하고 있습니다.
              </p>
              <ul class="section-list">
                <li>기술적 조치: AES-256 암호화 알고리즘을 통한 개인정보 암호화</li>
                <li>보안 통신: TLS(Transport Layer Security) 프로토콜을 통한 안전한 데이터 전송</li>
                <li>접근 제한: 개인정보에 대한 접근 권한을 최소한의 인원으로 제한</li>
                <li>접속 기록 보관: 개인정보 처리 시스템에 대한 접속 기록을 보관 및 점검</li>
              </ul>
            </section>

            <section class="info-card">
              <h2 class="section-title">제6조 (정보주체의 권리·의무 및 행사 방법)</h2>
              <p class="section-text">
                이용자는 개인정보 주체로서 다음과 같은 권리를 행사할 수 있습니다.
              </p>
              <ul class="section-list">
                <li>개인정보 열람 요구</li>
                <li>개인정보 정정 요구</li>
                <li>개인정보 삭제 요구</li>
                <li>개인정보 처리 정지 요구</li>
              </ul>
              <p class="section-text">
                위 권리 행사는 서비스 내 문의 기능을 통해 요청하실 수 있으며, 요청하신 내용에 대해 지체 없이 조치하겠습니다.
              </p>
            </section>

            <section class="info-card">
              <h2 class="section-title">제7조 (쿠키의 설치·운영 및 거부)</h2>
              <p class="section-text">
                서비스는 이용자에게 맞춤형 서비스를 제공하기 위해 쿠키를 사용합니다.
              </p>
              <ul class="section-list">
                <li>필수 쿠키: 서비스 제공을 위한 세션 유지 쿠키 (거부 시 서비스 이용 불가)</li>
                <li>분석 쿠키: Google Analytics를 통한 방문 통계 및 서비스 개선 (선택 사항)</li>
                <li>광고 쿠키: Kakao AdFit, LinkPrice 등 광고 파트너의 맞춤형 광고 제공 (선택 사항). 향후 Google AdSense 도입 시 별도 공지 후 적용됩니다.</li>
              </ul>
              <p class="section-text">
                이용자는 웹 브라우저 설정을 통해 쿠키 허용 여부를 선택하실 수 있습니다.
                단, 쿠키 설치를 거부할 경우 일부 서비스 이용에 어려움이 있을 수 있습니다.
              </p>
            </section>

            <section class="info-card">
              <h2 class="section-title">제8조 (개인정보 보호책임자 및 연락처)</h2>
              <p class="section-text">
                서비스는 개인정보 처리에 관한 업무를 총괄해서 책임지고, 개인정보 처리와 관련한 정보주체의 불만 처리 및 피해구제를 위하여 아래와 같이 개인정보 보호책임자를 지정하고 있습니다.
              </p>
              <ul class="section-list">
                <li>서비스명: 세라피나 (Serapina)</li>
                <li>웹사이트: https://www.serapina.kr</li>
                <li>문의 페이지: <router-link to="/contact">/contact</router-link></li>
              </ul>
              <p class="section-text">
                개인정보 보호와 관련하여 문의·신고가 있으시면 문의 페이지로 연락 주시기 바랍니다. 영업일 기준 24시간 안에 답변드립니다.
              </p>
            </section>

            <section class="info-card">
              <h2 class="section-title">제8-1조 (광고 및 제3자 서비스)</h2>
              <p class="section-text">
                본 서비스는 운영을 위해 다음 제3자 광고·분석 서비스를 사용합니다.
              </p>
              <ul class="section-list">
                <li><strong>Kakao AdFit</strong> — 디스플레이 배너 광고 (한국 사용자 대상, 쿠키·기기 식별자 기반)</li>
                <li><strong>LinkPrice</strong> — 어필리에이트(제휴) 링크를 통한 광고. 이용자가 링크를 클릭하여 외부 사이트에서 구매·가입 시 본 서비스에 수수료가 지급됩니다. 이용자에게 추가 비용은 발생하지 않습니다.</li>
                <li><strong>Google Analytics</strong> — 방문 통계 및 서비스 개선용 데이터 수집</li>
                <li><strong>Google AdSense</strong> — 향후 도입 예정. 도입 시 별도 공지 후 적용됩니다.</li>
              </ul>
              <p class="section-text">
                위 서비스들은 각각의 개인정보 처리방침에 따라 데이터를 처리합니다. 이용자는 브라우저 설정에서 쿠키 및 맞춤 광고를 거부할 수 있습니다.
              </p>
            </section>

            <section class="info-card">
              <h2 class="section-title">제9조 (개인정보 처리방침의 변경)</h2>
              <ul class="section-list">
                <li>본 개인정보 처리방침은 법령, 정책 또는 보안 기술의 변경에 따라 내용의 추가, 삭제 및 수정이 있을 수 있습니다</li>
                <li>개인정보 처리방침이 변경되는 경우 변경 사항은 서비스 화면을 통해 공지합니다</li>
                <li>변경된 개인정보 처리방침은 공지한 날로부터 효력이 발생합니다</li>
              </ul>
            </section>

            <section class="info-card">
              <p class="section-text" style="text-align: center; opacity: 0.8; margin: 0;">
                <strong>최종 수정일:</strong> 2026년 6월 12일
              </p>
            </section>
          </div>
        </div>

        <AdSenseBlock slot="1696071761" />
      </div>
  </div>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
import { useSeoMeta } from '@/composables/useSeoMeta'
import AdBanner from '@/components/AdBanner.vue'

useSeoMeta(
  '개인정보 처리방침 | 세라피나 타로',
  '세라피나 타로 서비스의 개인정보 수집, 이용, 보관, 보호에 관한 정책입니다. AES-256 암호화로 안전하게 보호됩니다.',
  '개인정보처리방침, 프라이버시, 데이터 보호, 타로 개인정보, 암호화'
)
</script>

<style scoped>
@import '@/assets/guide-pages.css';
</style>
