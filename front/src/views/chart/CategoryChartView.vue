<template>
  <div class="analysis-container">
    <SideBar />

    <div class="content-wrapper">
      <div class="filter-header">
        <div class="left-section">
          <button class="filter-btn active">
            <span v-if="accountStore.username">✓ {{ accountStore.username }} 님의 소비 분석</span>
          </button>
        </div>
      </div>

      <div class="category-analysis">
        <!-- 카테고리 도넛 차트 섹션 -->
        <div class="chart-section">
          <div class="donut-container">
            <CategoryChart @select-category="onSelectCategory" />
          </div>

          <!-- 카테고리 목록 -->
          <div class="category-list">
          </div>
        </div>

        <!-- 상세 내역 테이블 섹션 -->
        <div class="details-section">
          <CategoryList ref="categoryList" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import SideBar from "@/components/common/SideBar.vue";
import CategoryChart from "@/components/chart/CategoryChart.vue";
import CategoryList from "@/components/chart/CategoryList.vue";
import {ref, onMounted, onBeforeUnmount} from "vue";
import {useAccountStore} from "@/stores/accounts.js";

const categoryList = ref(null)
const accountStore = useAccountStore();

const onSelectCategory = (category) => {
  categoryList.value?.updateSelectedCategory(category)
}

// 스크롤 비활성화 및 복구 함수
const disableScroll = () => {
  document.body.style.overflow = 'hidden';
};

const enableScroll = () => {
  document.body.style.overflow = 'auto';
};

onMounted(() => {
  disableScroll(); // 컴포넌트가 마운트될 때 스크롤 비활성화
});

onBeforeUnmount(() => {
  enableScroll(); // 컴포넌트가 언마운트될 때 스크롤 복구
});

</script>

<style scoped>
.analysis-container {
  display: flex;
  min-height: 100vh;
  background: #f8f9fa;
}

.content-wrapper {
  flex: 1;
  padding: 32px;
  margin-left: 450px;
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

.category-analysis {
  max-height: 700px;
  display: flex;
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.chart-section {

  display: flex;
  margin-bottom: 32px;
}

.donut-container {
  width: 430px;
}



h3 {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin-bottom: 16px;
}

.category-list {
  flex: 1;
  padding: 20px 0;
}


.details-table th,
.details-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

.details-table th {
  font-weight: 500;
  color: #666;
  background: #f8f9fa;
}

.details-section {
  margin-left: 50px;
  width: 800px;
}
</style>