/**
 * Widget type definitions matching backend Pydantic models
 */

export enum WidgetType {
  IFRAME = 'iframe',
  SHORTCUT = 'shortcut',
}

export interface Widget {
  id: string
  type: WidgetType
  position: number
  properties: Record<string, unknown>
  created_at: string
  updated_at: string
}

export interface IframeWidgetProperties {
  url: string
  title: string
  width: number
  height: number
  refresh_interval?: number | null
}

export interface ShortcutWidgetProperties {
  url: string
  title: string
  icon: string
  description?: string | null
}

export interface CreateWidgetRequest {
  type: WidgetType
  properties: Record<string, unknown>
  position?: number | null
}

export interface UpdateWidgetRequest {
  properties: Record<string, unknown>
}

export interface UpdatePositionRequest {
  position: number
}

export interface DeleteWidgetResponse {
  status: string
  id: string
}
