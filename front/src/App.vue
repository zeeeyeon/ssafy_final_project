<template>
  <div class="main_div">
    <Navbar />

    <RouterView />
  </div>
</template>

<script setup>

import Navbar from "@/components/common/Navbar.vue";
import {RouterView} from "vue-router";
</script>

<style>
@font-face {
    font-family: 'Apple SD Gothic Neo';
    font-weight: 100;
    font-style: normal;
    font-display: swap;
    src: url('https://cdn.jsdelivr.net/gh/fonts-archive/AppleSDGothicNeo/AppleSDGothicNeo-Thin.woff2') format('woff2'),
         url('https://cdn.jsdelivr.net/gh/fonts-archive/AppleSDGothicNeo/AppleSDGothicNeo-Thin.ttf') format('truetype');
}
@font-face {
    font-family: 'Apple SD Gothic Neo';
    font-weight: 200;
    font-style: normal;
    font-display: swap;
    src: url('https://cdn.jsdelivr.net/gh/fonts-archive/AppleSDGothicNeo/AppleSDGothicNeo-ExtraLight.woff2') format('woff2'),
         url('https://cdn.jsdelivr.net/gh/fonts-archive/AppleSDGothicNeo/AppleSDGothicNeo-ExtraLight.ttf') format('truetype');
}
@font-face {
    font-family: 'Apple SD Gothic Neo';
    font-weight: 300;
    font-style: normal;
    font-display: swap;
    src: url('https://cdn.jsdelivr.net/gh/fonts-archive/AppleSDGothicNeo/AppleSDGothicNeo-Light.woff2') format('woff2'),
         url('https://cdn.jsdelivr.net/gh/fonts-archive/AppleSDGothicNeo/AppleSDGothicNeo-Light.ttf') format('truetype');
}
@font-face {
    font-family: 'Apple SD Gothic Neo';
    font-weight: 400;
    font-style: normal;
    font-display: swap;
    src: url('https://cdn.jsdelivr.net/gh/fonts-archive/AppleSDGothicNeo/AppleSDGothicNeo-Regular.woff2') format('woff2'),
         url('https://cdn.jsdelivr.net/gh/fonts-archive/AppleSDGothicNeo/AppleSDGothicNeo-Regular.ttf') format('truetype');
}
@font-face {
    font-family: 'Apple SD Gothic Neo';
    font-weight: 500;
    font-style: normal;
    font-display: swap;
    src: url('https://cdn.jsdelivr.net/gh/fonts-archive/AppleSDGothicNeo/AppleSDGothicNeo-Medium.woff2') format('woff2'),
         url('https://cdn.jsdelivr.net/gh/fonts-archive/AppleSDGothicNeo/AppleSDGothicNeo-Medium.ttf') format('truetype');
}
@font-face {
    font-family: 'Apple SD Gothic Neo';
    font-weight: 600;
    font-style: normal;
    font-display: swap;
    src: url('https://cdn.jsdelivr.net/gh/fonts-archive/AppleSDGothicNeo/AppleSDGothicNeo-SemiBold.woff2') format('woff2'),
         url('https://cdn.jsdelivr.net/gh/fonts-archive/AppleSDGothicNeo/AppleSDGothicNeo-SemiBold.ttf') format('truetype');
}
@font-face {
    font-family: 'Apple SD Gothic Neo';
    font-weight: 700;
    font-style: normal;
    font-display: swap;
    src: url('https://cdn.jsdelivr.net/gh/fonts-archive/AppleSDGothicNeo/AppleSDGothicNeo-Bold.woff2') format('woff2'),
         url('https://cdn.jsdelivr.net/gh/fonts-archive/AppleSDGothicNeo/AppleSDGothicNeo-Bold.ttf') format('truetype');
}
@font-face {
    font-family: 'Apple SD Gothic Neo';
    font-weight: 800;
    font-style: normal;
    font-display: swap;
    src: url('https://cdn.jsdelivr.net/gh/fonts-archive/AppleSDGothicNeo/AppleSDGothicNeo-ExtraBold.woff2') format('woff2'),
         url('https://cdn.jsdelivr.net/gh/fonts-archive/AppleSDGothicNeo/AppleSDGothicNeo-ExtraBold.ttf') format('truetype');
}
@font-face {
    font-family: 'Apple SD Gothic Neo';
    font-weight: 900;
    font-style: normal;
    font-display: swap;
    src: url('https://cdn.jsdelivr.net/gh/fonts-archive/AppleSDGothicNeo/AppleSDGothicNeo-Black.woff2') format('woff2'),
         url('https://cdn.jsdelivr.net/gh/fonts-archive/AppleSDGothicNeo/AppleSDGothicNeo-Black.ttf') format('truetype');
}
html, body {
    font-family: 'Apple SD Gothic Neo', sans-serif;
    font-weight: 400;
    padding: 0;
    margin: 0;
}

</style>