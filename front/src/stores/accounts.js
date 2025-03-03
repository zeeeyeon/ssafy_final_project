import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import { useRouter } from 'vue-router'
import axios from 'axios'

export const useAccountStore = defineStore('accounts', () => {
    const router = useRouter()
    const API_URL = 'http://127.0.0.1:8000'
    const token = ref(localStorage.getItem('auth'))
    const user = ref(null)
    const username = ref(null)

    // 로그인 상태 확인
    const isAuthenticated = computed(() => !!token.value)

    // 로그인
    const login = async (payload) => {
        const { email, password } = payload
        console.log(password)

        try {
            token.value = null
            user.value = null
            username.value = null

            const response = await axios({
                method: 'post',
                url: `${API_URL}/accounts/login/`,
                data: {
                    email,
                    password
                }
            })
            token.value = response.data.key
            localStorage.setItem('auth', response.data.key)
            await getUserInfo()
            await router.push({ name: 'Home' })
        } catch (error) {
            alert('정보를 다시 한번 확인해주세요!')
            console.error('로그인 실패:', error)
            throw error
        }
    }

    // 회원가입
    const register = async (payload) => {
        const {email, password1, password2, username, birth} = payload

        try {
            const response = await axios({
                method: 'post',
                url: `${API_URL}/accounts/registration/`,
                data: {
                    email, password1, password2, username, birth
                }
            })
            try {
                const res = await axios.get(`${API_URL}/account/books/`, {
                    headers: {
                        'Authorization': `Token ${response.data.key}`,
                    }
                });
                // 가계부 인스턴스가 성공적으로 존재할 때의 처리
                console.log('가계부 인스턴스 있음:', res.data);
            } catch (err) {
                // 오류 발생 시 처리
                if (err.res) {
                    // 서버에서 응답을 받은 경우, 응답 데이터와 상태 코드를 로그로 출력
                    console.error('가계부 인스턴스 에러:', err.response.data);
                    console.error('상태 코드:', err.response.status);
                } else {
                    // 서버에 도달하지 못한 경우 또는 응답을 받지 못한 경우
                    console.error('가계부 인스턴스 에러:', err.message);
                }
            }
            // token.value = response.data.key
            await login({email, password: password1})
            await router.push({name: 'Home'})
        } catch (error) {
            alert('회원가입에 실패했습니다. 입력 정보를 확인해주세요.')
            console.error('회원가입 실패:', error)
            throw error
        }
    }

    // 로그아웃
    const logout = async () => {
        try {
            await axios({
                method: 'post',
                url: `${API_URL}/accounts/logout/`
            })
            token.value = null
            user.value = null
            username.value = null
            // localStorage.removeItem('auth')
            localStorage.clear()
            router.push({ name: 'Home' })
        } catch (error) {
            console.error('로그아웃 실패:', error)
            throw error
        }
    }

    // 사용자 정보 가져오기 (마이 페이지)
    const getUserInfo = async () => {
        try {
            const response = await axios.get(`${API_URL}/accounts/user/`, {
                headers: { Authorization: `Token ${token.value}` }
            })
            console.log(token.value)
            user.value = response.data
            username.value = response.data.username
            // console.log(user)
            return response.data
        } catch (error) {
            console.error('사용자 정보 가져오기 실패:', error)
            throw error
        }
    }

    // 프로필 업데이트
    const updateProfile = async (userData) => {
        try {
            const response = await axios.put(`${API_URL}/accounts/profile/`, userData, {
                headers: { Authorization: `Token ${token.value}` }
            })
            user.value = response.data
            
        } catch (error) {
            console.error('프로필 업데이트 실패:', error)
            throw error
        }
    }


    return {
        user,
        isAuthenticated,
        username,
        login,
        register,
        logout,
        getUserInfo,
        updateProfile,
    }
}, { persist: true }) // 새로고침해도 상태 유지