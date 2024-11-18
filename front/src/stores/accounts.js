import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import { useRouter } from 'vue-router'
import axios from 'axios'

export const useAccountStore = defineStore('accounts', () => {
    const router = useRouter()
    const API_URL = 'http://127.0.0.1:8000'
    const token = ref(null)
    const user = ref(null)

    // 로그인 상태 확인
    const isAuthenticated = computed(() => !!token.value)

    // 로그인
    const login = async (payload) => {
        const { email, password } = payload

        try {
            const response = await axios({
                method: 'post',
                url: `${API_URL}/accounts/login/`,
                data: {
                    email,
                    password
                }
            })
            token.value = response.data.key
            router.push({ name: 'Home' })
        } catch (error) {
            alert('정보를 다시 한번 확인해주세요!')
            console.error('로그인 실패:', error)
            throw error
        }
    }

    // 회원가입
    const register = async (payload) => {
        const {email, password, username, birth} = payload

        try {
            const response = await axios({
                method: 'post',
                url: `${API_URL}/accounts/registration/`,
                data: {
                    email, password, username, birth
                }
            })
            // token.value = response.data.key
            login({ email, password })
            router.push({ name: 'Home' })
        } catch (error) {
            alert('회원가입에 실패했습니다. 입력 정보를 확인해주세요.')
            console.error('회원가입 실패:', error)
            throw error
        }
    }


    return {
        user,
        isAuthenticated,
        login,
        register
    }
}, { persist: true }) // 새로고침해도 상태 유지