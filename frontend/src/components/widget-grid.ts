/**
 * Widget grid component
 * Container for managing and displaying all widgets
 */

import { listWidgets, updateWidgetPosition } from '../services/widget-api'
import type { Widget } from '../types/widget'
import { WidgetType } from '../types/widget'
import './iframe-widget'
import './shortcut-widget'
import './query-widget'
import './widget-container'
import { WidgetContainer } from './widget-container'

export class WidgetGrid extends HTMLElement {
  private widgets: Widget[] = []
  private isLoading: boolean = false
  private containerOrder: WidgetType[] = []
  private readonly CONTAINER_ORDER_KEY = 'widget-container-order'
  private isEditMode: boolean = false

  connectedCallback(): void {
    this.loadContainerOrder()
    this.render()
    void this.loadWidgets()
    this.attachEventListeners()
  }

  /**
   * Load widgets from the API and render them
   */
  private async loadWidgets(): Promise<void> {
    this.isLoading = true
    this.render()

    try {
      this.widgets = await listWidgets()
      this.isLoading = false
      this.render()
    } catch (error) {
      console.error('Failed to load widgets:', error)
      this.isLoading = false
      this.renderError('Failed to load widgets. Please refresh the page.')
    }
  }

  /**
   * Refresh the widget list from the API
   */
  public async refresh(): Promise<void> {
    await this.loadWidgets()
  }

  /**
   * Render the grid and all widgets organized by container
   */
  private render(): void {
    if (this.isLoading) {
      this.innerHTML = `
        <div class="widget-grid-container">
          <div class="widget-grid-loading">
            <p>Loading widgets...</p>
          </div>
        </div>
      `
      return
    }

    this.innerHTML = `
      <div class="widget-grid-container ${this.isEditMode ? 'edit-mode' : ''}">
        <div class="widget-grid-header">
          <h1>Good Neighbor</h1>
          <div class="header-buttons">
            <button class="edit-mode-btn" title="${this.isEditMode ? 'Exit edit mode' : 'Edit shortcuts'}">
              ${this.isEditMode ? 'Done' : 'Edit'}
            </button>
            <button class="add-widget-btn" title="Add widget">+ Add Widget</button>
          </div>
        </div>
        <div class="widget-containers"></div>
      </div>
    `

    const containersArea = this.querySelector('.widget-containers')
    if (containersArea) {
      this.renderContainers(containersArea)
    }

    // Attach click handler to edit mode button
    const editButton = this.querySelector('.edit-mode-btn')
    if (editButton) {
      editButton.addEventListener('click', () => {
        this.isEditMode = !this.isEditMode
        this.render()
      })
    }

    // Attach click handler to add widget button
    const addButton = this.querySelector('.add-widget-btn')
    if (addButton) {
      addButton.addEventListener('click', () => {
        this.dispatchEvent(new CustomEvent('add-widget-requested', { bubbles: true }))
      })
    }
  }

  /**
   * Render widget containers grouped by type
   */
  private renderContainers(containersArea: Element): void {
    // Group widgets by type
    const widgetsByType = this.groupWidgetsByType()

    // Get available widget types (from widgets or default)
    const availableTypes = Array.from(widgetsByType.keys())

    // Ensure we have a default container order
    if (this.containerOrder.length === 0) {
      this.containerOrder = availableTypes
      this.saveContainerOrder()
    }

    // Add any new types that aren't in the order
    availableTypes.forEach((type) => {
      if (!this.containerOrder.includes(type)) {
        this.containerOrder.push(type)
      }
    })

    // Render containers in the specified order
    this.containerOrder.forEach((type) => {
      const widgets = widgetsByType.get(type)
      if (!widgets || widgets.length === 0) {
        return // Skip empty containers
      }

      const container = document.createElement('widget-container') as WidgetContainer
      container.setAttribute('type', type)
      containersArea.appendChild(container)

      // Add widgets to the container
      widgets.forEach((widget) => {
        const widgetElement = this.createWidgetElement(widget)
        if (widgetElement) {
          container.addWidget(widgetElement)
        }
      })
    })
  }

  /**
   * Group widgets by their type
   */
  private groupWidgetsByType(): Map<WidgetType, Widget[]> {
    const grouped = new Map<WidgetType, Widget[]>()

    this.widgets.forEach((widget) => {
      const type = widget.type
      if (!grouped.has(type)) {
        grouped.set(type, [])
      }
      grouped.get(type)!.push(widget)
    })

    return grouped
  }

  /**
   * Render an error message
   */
  private renderError(message: string): void {
    this.innerHTML = `
      <div class="widget-grid-container">
        <div class="widget-grid-error">
          <p>${this.escapeHtml(message)}</p>
          <button class="retry-btn">Retry</button>
        </div>
      </div>
    `

    const retryBtn = this.querySelector('.retry-btn')
    if (retryBtn) {
      retryBtn.addEventListener('click', () => {
        void this.loadWidgets()
      })
    }
  }

  /**
   * Create a widget element based on its type
   */
  private createWidgetElement(widget: Widget): HTMLElement | null {
    let element: HTMLElement | null = null

    switch (widget.type) {
      case WidgetType.IFRAME:
        element = document.createElement('iframe-widget')
        this.applyIframeProperties(element, widget)
        break
      case WidgetType.SHORTCUT:
        element = document.createElement('shortcut-widget')
        this.applyShortcutProperties(element, widget)
        break
      case WidgetType.QUERY:
        element = document.createElement('query-widget')
        this.applyQueryProperties(element, widget)
        break
      default: {
        const unknownType: string = widget.type as string
        console.warn(`Unknown widget type: ${unknownType}`)
        return null
      }
    }

    element.setAttribute('widget-id', widget.id)
    return element
  }

  /**
   * Apply iframe widget properties as attributes
   */
  private applyIframeProperties(element: HTMLElement, widget: Widget): void {
    const props = widget.properties
    if (props.url && typeof props.url === 'string') {
      element.setAttribute('url', props.url)
    }
    if (props.title && typeof props.title === 'string') {
      element.setAttribute('title', props.title)
    }
    if (props.width && typeof props.width === 'number') {
      element.setAttribute('width', props.width.toString())
    }
    if (props.height && typeof props.height === 'number') {
      element.setAttribute('height', props.height.toString())
    }
    if (props.refresh_interval && typeof props.refresh_interval === 'number') {
      element.setAttribute('refresh-interval', props.refresh_interval.toString())
    }
  }

  /**
   * Apply shortcut widget properties as attributes
   */
  private applyShortcutProperties(element: HTMLElement, widget: Widget): void {
    const props = widget.properties
    if (props.url && typeof props.url === 'string') {
      element.setAttribute('url', props.url)
    }
    if (props.title && typeof props.title === 'string') {
      element.setAttribute('title', props.title)
    }
    if (props.icon && typeof props.icon === 'string') {
      element.setAttribute('icon', props.icon)
    }
    if (props.description && typeof props.description === 'string') {
      element.setAttribute('description', props.description)
    }
  }

  /**
   * Apply query widget properties as attributes
   */
  private applyQueryProperties(element: HTMLElement, widget: Widget): void {
    const props = widget.properties
    if (props.url_template && typeof props.url_template === 'string') {
      element.setAttribute('url-template', props.url_template)
    }
    if (props.title && typeof props.title === 'string') {
      element.setAttribute('title', props.title)
    }
    if (props.icon && typeof props.icon === 'string') {
      element.setAttribute('icon', props.icon)
    }
    if (props.placeholder && typeof props.placeholder === 'string') {
      element.setAttribute('placeholder', props.placeholder)
    }
  }

  /**
   * Attach event listeners for widget events
   */
  private attachEventListeners(): void {
    // Listen for widget deletion events
    this.addEventListener('widget-deleted', ((event: Event) => {
      const customEvent = event as CustomEvent<{ widgetId: string }>
      const widgetId = customEvent.detail.widgetId
      this.widgets = this.widgets.filter((w) => w.id !== widgetId)
      // Re-render to update container widget counts
      this.render()
    }) as EventListener)

    // Listen for widget update events
    this.addEventListener('widget-updated', ((event: Event) => {
      const customEvent = event as CustomEvent<{ widgetId: string; properties: Record<string, unknown> }>
      const widgetId = customEvent.detail.widgetId
      const properties = customEvent.detail.properties
      const widget = this.widgets.find((w) => w.id === widgetId)
      if (widget) {
        widget.properties = properties
        widget.updated_at = new Date().toISOString()
      }
    }) as EventListener)

    // Listen for container reorder events
    this.addEventListener('container-reorder', ((event: Event) => {
      const customEvent = event as CustomEvent<{
        draggedType: WidgetType
        targetType: WidgetType
        position: 'before' | 'after'
      }>
      this.handleContainerReorder(
        customEvent.detail.draggedType,
        customEvent.detail.targetType,
        customEvent.detail.position
      )
    }) as EventListener)

    // Listen for widget reorder events
    this.addEventListener('widget-reorder', ((event: Event) => {
      const customEvent = event as CustomEvent<{
        draggedWidgetId: string
        targetWidgetId: string
        position: 'before' | 'after'
      }>
      void this.handleWidgetReorder(
        customEvent.detail.draggedWidgetId,
        customEvent.detail.targetWidgetId,
        customEvent.detail.position
      )
    }) as EventListener)
  }

  /**
   * Handle container reordering via drag and drop
   */
  private handleContainerReorder(
    draggedType: WidgetType,
    targetType: WidgetType,
    position: 'before' | 'after'
  ): void {
    // Remove the dragged type from its current position
    const draggedIndex = this.containerOrder.indexOf(draggedType)
    if (draggedIndex === -1) return

    this.containerOrder.splice(draggedIndex, 1)

    // Find the new position
    const targetIndex = this.containerOrder.indexOf(targetType)
    if (targetIndex === -1) return

    // Insert at the new position
    const insertIndex = position === 'before' ? targetIndex : targetIndex + 1
    this.containerOrder.splice(insertIndex, 0, draggedType)

    // Save the new order and re-render
    this.saveContainerOrder()
    this.render()
  }

  /**
   * Handle widget reordering within a container via drag and drop
   */
  private async handleWidgetReorder(
    draggedWidgetId: string,
    targetWidgetId: string,
    position: 'before' | 'after'
  ): Promise<void> {
    const draggedWidget = this.widgets.find((w) => w.id === draggedWidgetId)
    const targetWidget = this.widgets.find((w) => w.id === targetWidgetId)

    if (!draggedWidget || !targetWidget) {
      console.error('Widget not found for reordering')
      return
    }

    // Only allow reordering within the same type
    if (draggedWidget.type !== targetWidget.type) {
      console.warn('Cannot reorder widgets of different types')
      return
    }

    // Get all widgets of the same type, sorted by position
    const sameTypeWidgets = this.widgets
      .filter((w) => w.type === draggedWidget.type)
      .sort((a, b) => a.position - b.position)

    // Find indices
    const draggedIndex = sameTypeWidgets.findIndex((w) => w.id === draggedWidgetId)
    const targetIndex = sameTypeWidgets.findIndex((w) => w.id === targetWidgetId)

    if (draggedIndex === -1 || targetIndex === -1) return

    // Remove dragged widget from its current position
    const [movedWidget] = sameTypeWidgets.splice(draggedIndex, 1)

    // Calculate new insert position
    let insertIndex = targetIndex
    if (draggedIndex < targetIndex && position === 'after') {
      insertIndex = targetIndex // Already adjusted by removal
    } else if (draggedIndex < targetIndex && position === 'before') {
      insertIndex = targetIndex - 1
    } else if (draggedIndex > targetIndex && position === 'after') {
      insertIndex = targetIndex + 1
    } else {
      insertIndex = targetIndex // before, and dragged is after target
    }

    // Insert at new position
    sameTypeWidgets.splice(insertIndex, 0, movedWidget)

    // Update positions in backend
    try {
      // Update positions for all widgets of this type
      const updatePromises = sameTypeWidgets.map((widget, index) => {
        widget.position = index
        return updateWidgetPosition(widget.id, { position: index })
      })

      await Promise.all(updatePromises)

      // Re-render to show new order
      await this.loadWidgets()
    } catch (error) {
      console.error('Failed to update widget positions:', error)
      alert('Failed to reorder widgets. Please try again.')
    }
  }

  /**
   * Load container order from localStorage
   */
  private loadContainerOrder(): void {
    try {
      const stored = localStorage.getItem(this.CONTAINER_ORDER_KEY)
      if (stored) {
        this.containerOrder = JSON.parse(stored) as WidgetType[]
      }
    } catch (error) {
      console.error('Failed to load container order:', error)
      this.containerOrder = []
    }
  }

  /**
   * Save container order to localStorage
   */
  private saveContainerOrder(): void {
    try {
      localStorage.setItem(this.CONTAINER_ORDER_KEY, JSON.stringify(this.containerOrder))
    } catch (error) {
      console.error('Failed to save container order:', error)
    }
  }

  /**
   * Escape HTML to prevent XSS
   */
  private escapeHtml(text: string): string {
    const div = document.createElement('div')
    div.textContent = text
    return div.innerHTML
  }
}

// Register custom element
customElements.define('widget-grid', WidgetGrid)
