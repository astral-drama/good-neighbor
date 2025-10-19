/**
 * Homepage type definitions
 */

export interface Homepage {
  homepage_id: string
  user_id: string
  name: string
  is_default: boolean
  created_at: string
  updated_at: string
}

export interface CreateHomepageRequest {
  name: string
  is_default?: boolean
}

export interface UpdateHomepageRequest {
  name: string
}
