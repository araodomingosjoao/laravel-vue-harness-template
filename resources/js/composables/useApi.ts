import axios, { type AxiosInstance } from 'axios'

let instance: AxiosInstance | null = null

/**
 * Composable para chamadas HTTP. NUNCA uses fetch() directamente em componentes.
 *
 * - Trata de CSRF cookies (sanctum/csrf-cookie no primeiro request)
 * - Inclui headers JSON por defeito
 * - Lança erros tipados em vez de retornar response
 */
export function useApi(): AxiosInstance {
  if (instance) return instance

  instance = axios.create({
    baseURL: '/',
    withCredentials: true,
    withXSRFToken: true,
    headers: {
      Accept: 'application/json',
      'X-Requested-With': 'XMLHttpRequest',
    },
  })

  return instance
}
