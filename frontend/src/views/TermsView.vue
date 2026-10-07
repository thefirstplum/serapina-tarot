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
              <h1 class="page-title">{{ t('legal.terms.title') }}</h1>
              <p class="page-subtitle">{{ t('legal.terms.subtitle') }}</p>
            </div>
          </div>
        </div>

        <!-- Content -->
        <div class="page-content">
          <div class="content-container">
            <section class="info-card">
              <h2 class="section-title">제1조 (목적)</h2>
              <p class="section-text">
                본 약관은 세라피나 타로(이하 "서비스")가 제공하는 AI 기반 타로 리딩 서비스의 이용과 관련하여
                서비스 제공자와 이용자 간의 권리, 의무 및 책임사항, 기타 필요한 사항을 규정함을 목적으로 합니다.
              </p>
            </section>

            <section class="info-card">
              <h2 class="section-title">제2조 (서비스의 내용)</h2>
              <p class="section-text">
                본 서비스는 인공지능(AI) 기술을 활용한 타로 카드 해석 서비스를 제공합니다.
              </p>
              <ul class="section-list">
                <li>사용자의 질문에 대한 AI 기반 타로 카드 해석</li>
                <li>질문 성격에 맞춰 1장 또는 다수의 카드를 활용한 리딩</li>
                <li>대화형 인터페이스를 통한 타로 상담</li>
                <li>타로 카드 의미 및 해석 정보 제공</li>
                <li>블로그에 게시되는 상담 사례는 운영자가 작성한 가상의 시나리오이거나, 실제 사례를 익명화·각색·재구성한 콘텐츠이며, 특정 이용자의 상담 내용이 식별 가능한 형태로 게시되지 않습니다</li>
              </ul>
            </section>

            <section class="info-card">
              <h2 class="section-title">제3조 (이용자의 의무)</h2>
              <p class="section-text">
                이용자는 다음 행위를 하여서는 안 됩니다.
              </p>
              <ul class="section-list">
                <li>타인의 개인정보를 도용하거나 부정하게 사용하는 행위</li>
                <li>서비스의 정상적인 운영을 방해하는 행위</li>
                <li>범죄적 행위에 관련되는 행위 또는 선량한 풍속 기타 사회질서에 반하는 행위</li>
                <li>다른 이용자 또는 제3자의 명예를 훼손하거나 업무를 방해하는 행위</li>
                <li>서비스를 영리 목적으로 무단 이용하는 행위</li>
                <li>저작권 등 타인의 지적재산권을 침해하는 행위</li>
              </ul>
            </section>

            <section class="info-card">
              <h2 class="section-title">제4조 (서비스 이용 시 주의사항)</h2>
              <div class="alert-box">
                본 서비스에서 제공하는 타로 카드 해석은 참고용 가이드라인이며, 절대적인 미래 예측이 아닙니다.
                중요한 결정을 내리실 때에는 충분한 고민과 전문가의 상담을 통해 신중하게 판단하시기 바랍니다.
              </div>
              <ul class="section-list">
                <li>건강, 법률, 재무 관련 문제는 반드시 해당 분야의 전문가와 상담하시기 바랍니다</li>
                <li>민감한 개인정보(주민등록번호, 계좌번호, 비밀번호 등)는 입력하지 마십시오</li>
                <li>본 서비스는 엔터테인먼트 목적의 참고 자료로만 활용하시기 바랍니다</li>
                <li>만 14세 미만의 이용자는 법정대리인의 동의가 필요합니다</li>
                <li>본 서비스는 전문 상담(심리, 법률, 의료 등)을 대체할 수 없습니다</li>
              </ul>
            </section>

            <section class="info-card">
              <h2 class="section-title">제5조 (면책사항)</h2>
              <ul class="section-list">
                <li>서비스는 엔터테인먼트 목적으로 제공되며, 의료·법률·투자 등 전문적인 조언을 제공하지 않습니다</li>
                <li>타로 해석 결과에 대한 모든 책임은 이용자 본인에게 있습니다</li>
                <li>서비스 이용으로 인해 발생한 직접적, 간접적, 부수적, 특별한 손해에 대해 책임을 지지 않습니다</li>
                <li>천재지변, 시스템 장애 등 불가항력적 사유로 인한 서비스 중단 시 책임을 지지 않습니다</li>
              </ul>
            </section>

            <section class="info-card">
              <h2 class="section-title">제6조 (저작권 및 지적재산권)</h2>
              <ul class="section-list">
                <li>서비스 내 모든 콘텐츠(텍스트, 이미지, 소프트웨어 등)의 저작권은 서비스 제공자에게 있습니다</li>
                <li>타로 카드 이미지는 운영자가 AI 이미지 생성 도구를 활용해 직접 디자인한 자체 일러스트입니다 (78장 전체, 사용된 도구의 약관에 따라 상업적 이용이 허용된 결과물)</li>
                <li>이용자는 서비스를 통해 제공받은 콘텐츠를 개인적 용도로만 사용할 수 있습니다</li>
                <li>상업적 이용, 재배포, 2차 저작물 제작은 사전 서면 허가가 필요합니다</li>
              </ul>
            </section>

            <section class="info-card">
              <h2 class="section-title">제7조 (개인정보 보호)</h2>
              <p class="section-text">
                서비스는 관련 법령이 정하는 바에 따라 이용자의 개인정보를 보호하기 위해 노력합니다.
                개인정보의 수집, 이용, 보관, 파기 등에 관한 사항은 개인정보 처리방침에 따릅니다.
              </p>
            </section>

            <section class="info-card">
              <h2 class="section-title">제8조 (약관의 변경)</h2>
              <ul class="section-list">
                <li>서비스 제공자는 필요한 경우 관련 법령을 위배하지 않는 범위에서 본 약관을 변경할 수 있습니다</li>
                <li>약관이 변경되는 경우 변경 내용과 적용일자를 서비스 화면에 공지합니다</li>
                <li>변경된 약관은 공지된 적용일자부터 효력이 발생합니다</li>
              </ul>
            </section>

            <section class="info-card">
              <h2 class="section-title">제9조 (분쟁의 해결)</h2>
              <p class="section-text">
                본 약관과 관련하여 분쟁이 발생한 경우 당사자 간 성실한 협의를 통해 해결하도록 노력하며,
                협의가 이루어지지 않을 경우 대한민국 법률을 준거법으로 하며, 관할 법원은 민사소송법상의 관할 법원으로 합니다.
              </p>
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
  '서비스 이용약관 | 세라피나 타로',
  '세라피나 타로 서비스 이용 규칙, 주의사항, 면책사항 등 이용약관입니다. 타로 AI 해석은 참고 목적의 엔터테인먼트 서비스입니다.',
  '이용약관, 서비스 약관, 타로 이용규칙, 면책사항'
)
</script>

<style scoped>
@import '@/assets/guide-pages.css';
</style>
