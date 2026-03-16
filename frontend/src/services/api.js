import axios from 'axios'

let tokenGetter = () => null
let unauthorizedHandler = null

export const setAuthTokenGetter = (getter) => {
  tokenGetter = getter
}

export const setUnauthorizedHandler = (handler) => {
  unauthorizedHandler = handler
}

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
})

api.interceptors.request.use((config) => {
  const token = tokenGetter()
  const shouldSkipAuth = config.headers?.['X-Skip-Auth']

  if (token && !shouldSkipAuth) {
    config.headers.Authorization = `Bearer ${token}`
  }

  if (config.headers?.['X-Skip-Auth']) {
    delete config.headers['X-Skip-Auth']
  }

  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      if (unauthorizedHandler) {
        unauthorizedHandler()
      } else {
        window.location.href = '/login'
      }
    }

    return Promise.reject(error)
  },
)

export default api
