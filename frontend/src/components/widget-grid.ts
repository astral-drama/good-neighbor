/**
 * Widget grid component
 * Container for managing and displaying all widgets
 */

import { listWidgets } from '../services/widget-api'
import type { Widget } from '../types/widget'
import { WidgetType } from '../types/widget'
import './iframe-widget'
import './shortcut-widget'

export class WidgetGrid extends HTMLElement {
  private widgets: Widget[] = []
  private isLoading: boolean = false

  connectedCallback(): void {
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
   * Render the grid and all widgets
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
      <div class="widget-grid-container">
        <div class="widget-grid-header">
          <h1>Good Neighbor</h1>
          <button class="add-widget-btn" title="Add widget">+ Add Widget</button>
        </div>
        <div class="widget-grid"></div>
      </div>
    `

    const grid = this.querySelector('.widget-grid')
    if (grid) {
      this.widgets.forEach((widget) => {
        const widgetElement = this.createWidgetElement(widget)
        if (widgetElement) {
          grid.appendChild(widgetElement)
        }
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
   * Attach event listeners for widget events
   */
  private attachEventListeners(): void {
    // Listen for widget deletion events
    this.addEventListener('widget-deleted', ((event: Event) => {
      const customEvent = event as CustomEvent<{ widgetId: string }>
      const widgetId = customEvent.detail.widgetId
      this.widgets = this.widgets.filter((w) => w.id !== widgetId)
      // No need to re-render, the widget already removed itself from DOM
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
