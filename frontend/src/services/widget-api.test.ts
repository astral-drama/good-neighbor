import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { listWidgets, createWidget, getWidget, updateWidget, updateWidgetPosition, deleteWidget } from './widget-api'
import type { Widget, CreateWidgetRequest, UpdateWidgetRequest, UpdatePositionRequest } from '../types/widget'
import { WidgetType } from '../types/widget'

describe('Widget API Service', () => {
  const mockFetch = vi.fn()

  beforeEach(() => {
    vi.stubGlobal('fetch', mockFetch)
    mockFetch.mockClear()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe('listWidgets', () => {
    it('should fetch all widgets', async () => {
      const mockWidgets: Widget[] = [
        {
          id: '1',
          type: WidgetType.IFRAME,
          position: 0,
          properties: { url: 'https://example.com', title: 'Test' },
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z',
        },
      ]

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockWidgets),
      })

      const result = await listWidgets()

      expect(mockFetch).toHaveBeenCalledWith('/api/widgets')
      expect(result).toEqual(mockWidgets)
    })

    it('should throw error on failed request', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        statusText: 'Internal Server Error',
      })

      await expect(listWidgets()).rejects.toThrow('Failed to fetch widgets')
    })
  })

  describe('createWidget', () => {
    it('should create a new widget', async () => {
      const request: CreateWidgetRequest = {
        type: WidgetType.SHORTCUT,
        properties: {
          url: 'https://example.com',
          title: 'Test Shortcut',
          icon: '🔗',
        },
      }

      const mockWidget: Widget = {
        id: 'new-123',
        type: WidgetType.SHORTCUT,
        position: 0,
        properties: request.properties,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      }

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockWidget),
      })

      const result = await createWidget(request)

      expect(mockFetch).toHaveBeenCalledWith('/api/widgets', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      })
      expect(result).toEqual(mockWidget)
    })

    it('should throw error on failed creation', async () => {
      const request: CreateWidgetRequest = {
        type: WidgetType.IFRAME,
        properties: {},
      }

      mockFetch.mockResolvedValueOnce({
        ok: false,
        statusText: 'Bad Request',
      })

      await expect(createWidget(request)).rejects.toThrow('Failed to create widget')
    })
  })

  describe('getWidget', () => {
    it('should fetch a specific widget by ID', async () => {
      const mockWidget: Widget = {
        id: 'test-123',
        type: WidgetType.IFRAME,
        position: 0,
        properties: { url: 'https://example.com', title: 'Test' },
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      }

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockWidget),
      })

      const result = await getWidget('test-123')

      expect(mockFetch).toHaveBeenCalledWith('/api/widgets/test-123')
      expect(result).toEqual(mockWidget)
    })

    it('should throw error when widget not found', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        statusText: 'Not Found',
      })

      await expect(getWidget('nonexistent')).rejects.toThrow('Failed to fetch widget')
    })
  })

  describe('updateWidget', () => {
    it('should update widget properties', async () => {
      const request: UpdateWidgetRequest = {
        properties: {
          url: 'https://updated.com',
          title: 'Updated Title',
        },
      }

      const mockWidget: Widget = {
        id: 'test-123',
        type: WidgetType.IFRAME,
        position: 0,
        properties: request.properties,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T12:00:00Z',
      }

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockWidget),
      })

      const result = await updateWidget('test-123', request)

      expect(mockFetch).toHaveBeenCalledWith('/api/widgets/test-123', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      })
      expect(result).toEqual(mockWidget)
    })
  })

  describe('updateWidgetPosition', () => {
    it('should update widget position', async () => {
      const request: UpdatePositionRequest = {
        position: 5,
      }

      const mockWidget: Widget = {
        id: 'test-123',
        type: WidgetType.IFRAME,
        position: 5,
        properties: {},
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T12:00:00Z',
      }

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockWidget),
      })

      const result = await updateWidgetPosition('test-123', request)

      expect(mockFetch).toHaveBeenCalledWith('/api/widgets/test-123/position', {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      })
      expect(result.position).toBe(5)
    })
  })

  describe('deleteWidget', () => {
    it('should delete a widget', async () => {
      const mockResponse = {
        status: 'deleted',
        id: 'test-123',
      }

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockResponse),
      })

      const result = await deleteWidget('test-123')

      expect(mockFetch).toHaveBeenCalledWith('/api/widgets/test-123', {
        method: 'DELETE',
      })
      expect(result).toEqual(mockResponse)
    })

    it('should throw error on failed deletion', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        statusText: 'Not Found',
      })

      await expect(deleteWidget('nonexistent')).rejects.toThrow('Failed to delete widget')
    })
  })
})
