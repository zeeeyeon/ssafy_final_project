<template>
  <div class="analysis-container">
    <SideBar />

    <div class="filter-header">
      <div class="left-section">
        <button class="filter-btn active">
          <span v-if="accountStore.username">✓ {{ accountStore.username }} 님의 소비 분석</span>
        </button>
      </div>
    </div>

    <div class="analysis-content">
      <div class="month_container">
        <!-- 1. 월별 총액 요약 컨테이너 -->
        <MonthlyChart />

        <!-- 2. 11월 분석 그래프 컨테이너 -->
        <div class="chart-container">
            <MonthlyBudgetChart />

        </div>

      </div>

      <div class="weekly_container">
        <!-- 3. 주간별 상세 내역 컨테이너 -->
        <WeeklyChart />

        <!-- 4. 고정 지출 분석 컨테이너 -->
        <div class="fixed-expense-container">
          <h3>소비핑의 쓴소리</h3>
          <DataEvaluation />
        </div>
      </div>
      
    
    </div>
  </div>
</template>

<script setup>
import SideBar from "@/components/common/SideBar.vue";
import MonthlyChart from "@/components/chart/MonthlyChart.vue";
import WeeklyChart from "@/components/chart/WeeklyChart.vue";
import MonthlyBudgetChart from "@/components/chart/MonthlyBudgetChart.vue";
import DataEvaluation from "@/components/chart/DataEvaluation.vue";
import {useAccountStore} from "@/stores/accounts.js";

const accountStore = useAccountStore();
</script>

<style scoped>
.analysis-container {
  padding: 32px;
  margin-left: 480px;
  max-width: 1300px;
  background: white;
}

.analysis-content {
  display: flex;
  flex-direction: column ;
  gap: 24px;
}

.month_container {
  max-width: 1300px;
  height: 300px;
  display: flex;
}
.weekly_container {
  display: flex;
  height: 300px;
}

.filter-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.filter-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border: 1px solid #ddd;
  border-radius: 20px;
  background: white;
}

.filter-btn.active {
  background: #f0f0f0;
}

/* 1. 월별 총액 요약 컨테이너 */
.summary-container {
  background: white;
  /* 위칸 첫번째 컨테이너 넓이 */
  width: 400px;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

/* 2. 월별 분석 그래프 컨테이너 */
.chart-container {
  /* 옆 상자 간결 */
  margin-left: 50px;
  /* 위칸 두번째 컨테이너 넓이 */
  width: 650px;
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

/* 3. 주간별 상세 내역 컨테이너 */
.weekly-details-container {
  /* 아래칸 첫번째 컨테이너 넓이 */
  width: 850px;
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

/* 4. 고정 지출 분석 컨테이너 */
.fixed-expense-container {
  /* 옆 상자 간결 */
  margin-left: 50px;
  /* 아래칸 두번째 컨테이너 넓이 */
  width: 650px;
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

/* 공통 스타일 */
h3 {
  font-size: 18px;
  font-weight: 600;
  color: #1a1438;
  margin-bottom: 16px;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.chart-legend {
  display: flex;
  gap: 16px;
  font-size: 14px;
}

</style>
