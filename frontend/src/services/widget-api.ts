/**
 * Widget API client for communicating with backend
 */

import type {
  CreateWidgetRequest,
  DeleteWidgetResponse,
  UpdatePositionRequest,
  UpdateWidgetRequest,
  Widget,
} from '../types/widget'

const API_BASE = `${import.meta.env.BASE_URL}api/widgets`.replace('//', '/')

/**
 * Fetch all widgets from the backend
 */
export async function listWidgets(): Promise<Widget[]> {
  const response = await fetch(API_BASE)
  if (!response.ok) {
    throw new Error(`Failed to fetch widgets: ${response.statusText}`)
  }
  return (await response.json()) as Widget[]
}

/**
 * Create a new widget
 */
export async function createWidget(request: CreateWidgetRequest): Promise<Widget> {
  const response = await fetch(API_BASE, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  })

  if (!response.ok) {
    throw new Error(`Failed to create widget: ${response.statusText}`)
  }
  return (await response.json()) as Widget
}

/**
 * Get a specific widget by ID
 */
export async function getWidget(widgetId: string): Promise<Widget> {
  const response = await fetch(`${API_BASE}/${widgetId}`)
  if (!response.ok) {
    throw new Error(`Failed to fetch widget: ${response.statusText}`)
  }
  return (await response.json()) as Widget
}

/**
 * Update widget properties
 */
export async function updateWidget(widgetId: string, request: UpdateWidgetRequest): Promise<Widget> {
  const response = await fetch(`${API_BASE}/${widgetId}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  })

  if (!response.ok) {
    throw new Error(`Failed to update widget: ${response.statusText}`)
  }
  return (await response.json()) as Widget
}

/**
 * Update widget position
 */
export async function updateWidgetPosition(
  widgetId: string,
  request: UpdatePositionRequest,
): Promise<Widget> {
  const response = await fetch(`${API_BASE}/${widgetId}/position`, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  })

  if (!response.ok) {
    throw new Error(`Failed to update widget position: ${response.statusText}`)
  }
  return (await response.json()) as Widget
}

/**
 * Delete a widget
 */
export async function deleteWidget(widgetId: string): Promise<DeleteWidgetResponse> {
  const response = await fetch(`${API_BASE}/${widgetId}`, {
    method: 'DELETE',
  })

  if (!response.ok) {
    throw new Error(`Failed to delete widget: ${response.statusText}`)
  }
  return (await response.json()) as DeleteWidgetResponse
}
