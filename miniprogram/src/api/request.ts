/**
 * API 请求封装
 * 统一处理请求拦截、响应解析、错误处理、自动重试
 */

// API 基础地址 (开发环境)
const BASE_URL = 'http://localhost:8000/api/v1'

// 最大重试次数
const MAX_RETRY = 2
// 请求超时时间 (ms)
const REQUEST_TIMEOUT = 15000

interface RequestOptions {
  url: string
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE'
  data?: Record<string, any>
  header?: Record<string, string>
  showLoading?: boolean
  retry?: boolean
  silent?: boolean // 静默模式，不弹toast
}

interface ApiResponse<T = any> {
  code: number
  message: string
  data: T
}

/** 检查网络状态 */
function checkNetwork(): Promise<boolean> {
  return new Promise((resolve) => {
    uni.getNetworkType({
      success: (res) => resolve(res.networkType !== 'none'),
      fail: () => resolve(true), // 检测失败默认认为有网
    })
  })
}

/**
 * 统一请求方法
 */
export async function request<T = any>(options: RequestOptions): Promise<ApiResponse<T>> {
  const {
    url, method = 'GET', data, header = {},
    showLoading = false, retry = false, silent = false
  } = options

  // 网络检查
  const hasNetwork = await checkNetwork()
  if (!hasNetwork) {
    if (!silent) {
      uni.showToast({ title: '当前无网络连接', icon: 'none' })
    }
    return Promise.reject(new Error('NO_NETWORK'))
  }

  // 从本地缓存读取 token
  const token = uni.getStorageSync('auth_token')
  if (token) {
    header['Authorization'] = `Bearer ${token}`
  }

  if (showLoading) {
    uni.showLoading({ title: '加载中...', mask: true })
  }

  return doRequest<T>(url, method, data, header, showLoading, retry ? MAX_RETRY : 0, silent)
}

function doRequest<T>(
  url: string,
  method: string,
  data: any,
  header: Record<string, string>,
  showLoading: boolean,
  retryCount: number,
  silent: boolean,
): Promise<ApiResponse<T>> {
  return new Promise((resolve, reject) => {
    uni.request({
      url: `${BASE_URL}${url}`,
      method: method as any,
      data,
      header: {
        'Content-Type': 'application/json',
        ...header,
      },
      timeout: REQUEST_TIMEOUT,
      success: (res) => {
        if (showLoading) uni.hideLoading()

        const body = res.data as ApiResponse<T>
        if (body.code === 0) {
          resolve(body)
        } else if (body.code === 401) {
          // Token 过期，清除登录态
          uni.removeStorageSync('auth_token')
          if (!silent) {
            uni.showToast({ title: '登录已过期，请重新登录', icon: 'none' })
          }
          reject(body)
        } else {
          if (!silent) {
            uni.showToast({ title: body.message || '请求失败', icon: 'none' })
          }
          reject(body)
        }
      },
      fail: (err) => {
        if (showLoading) uni.hideLoading()

        // 可重试则重试
        if (retryCount > 0) {
          setTimeout(() => {
            doRequest<T>(url, method, data, header, false, retryCount - 1, silent)
              .then(resolve)
              .catch(reject)
          }, 1000)
          return
        }

        // 超时判断
        const isTimeout = err.errMsg?.includes('timeout')
        if (!silent) {
          uni.showToast({
            title: isTimeout ? '请求超时，请检查网络' : '网络连接异常',
            icon: 'none',
          })
        }

        // 上报错误
        try {
          uni.request({
            url: `${BASE_URL}/events/error`,
            method: 'POST',
            data: {
              errorType: isTimeout ? 'api_timeout' : 'api_error',
              detail: err.errMsg || 'unknown',
              url,
              method,
            },
          })
        } catch (e) { /* ignore */ }

        reject(err)
      },
    })
  })
}

/**
 * 便捷方法
 */
export const api = {
  get: <T = any>(url: string, data?: Record<string, any>, silent = false) =>
    request<T>({ url, method: 'GET', data, silent }),

  post: <T = any>(url: string, data?: Record<string, any>, showLoading = false, silent = false) =>
    request<T>({ url, method: 'POST', data, showLoading, silent }),

  put: <T = any>(url: string, data?: Record<string, any>) =>
    request<T>({ url, method: 'PUT', data }),

  delete: <T = any>(url: string) =>
    request<T>({ url, method: 'DELETE' }),
}
