/**
 * Query widget component
 * Allows users to submit text queries to configurable URLs
 */

import { BaseWidget } from './base-widget'
import type { QueryWidgetProperties } from '../types/widget'

export class QueryWidget extends BaseWidget {
  private faviconCache: Map<string, string> = new Map()
  private isFetchingFavicon = false

  static get observedAttributes(): string[] {
    return ['url-template', 'title', 'icon', 'placeholder']
  }

  connectedCallback(): void {
    super.connectedCallback()
    this.autoFetchFavicon()
  }

  attributeChangedCallback(name: string, oldValue: string | null, newValue: string | null): void {
    // Auto-fetch favicon when URL template changes
    if (name === 'url-template' && oldValue !== newValue) {
      this.autoFetchFavicon()
    }
  }

  protected render(): void {
    switch (this.state) {
      case 'normal':
        this.renderNormalView()
        break
      case 'hover':
        this.renderHoverView()
        break
      case 'edit':
        this.renderEditView()
        break
    }
  }

  private renderNormalView(): void {
    const title = this.getAttribute('title') || 'Search'
    const icon = this.getAttribute('icon') || '🔍'
    const placeholder = this.getAttribute('placeholder') || 'Enter query...'

    const iconHtml = this.renderIcon(icon)

    this.innerHTML = `
      <div class="widget-container query-widget">
        <form class="query-form" style="display: flex; align-items: center; gap: 0.5rem; width: 100%;">
          <span class="query-icon" title="${this.escapeHtml(title)}" style="flex-shrink: 0; display: flex; align-items: center; font-size: 1.5rem;">
            ${iconHtml}
          </span>
          <input
            type="text"
            class="query-input"
            placeholder="${this.escapeHtml(placeholder)}"
            autocomplete="off"
            style="flex: 1; min-width: 0;"
          />
          <button type="submit" class="query-submit-btn" title="Submit query" style="flex-shrink: 0;">→</button>
        </form>
      </div>
    `

    // Add form submit handler
    const form = this.querySelector('.query-form') as HTMLFormElement
    if (form) {
      form.addEventListener('submit', (e) => {
        e.preventDefault()
        this.handleQuerySubmit()
      })
    }
  }

  private renderHoverView(): void {
    const title = this.getAttribute('title') || 'Search'
    const icon = this.getAttribute('icon') || '🔍'
    const placeholder = this.getAttribute('placeholder') || 'Enter query...'

    const iconHtml = this.renderIcon(icon)

    this.innerHTML = `
      <div class="widget-container query-widget widget-hover">
        <div class="widget-action-buttons"></div>
        <form class="query-form" style="display: flex; align-items: center; gap: 0.5rem; width: 100%;">
          <span class="query-icon" title="${this.escapeHtml(title)}" style="flex-shrink: 0; display: flex; align-items: center; font-size: 1.5rem;">
            ${iconHtml}
          </span>
          <input
            type="text"
            class="query-input"
            placeholder="${this.escapeHtml(placeholder)}"
            autocomplete="off"
            style="flex: 1; min-width: 0;"
          />
          <button type="submit" class="query-submit-btn" title="Submit query" style="flex-shrink: 0;">→</button>
        </form>
      </div>
    `

    // Add form submit handler
    const form = this.querySelector('.query-form') as HTMLFormElement
    if (form) {
      form.addEventListener('submit', (e) => {
        e.preventDefault()
        this.handleQuerySubmit()
      })
    }

    // Add action buttons
    const container = this.querySelector('.widget-action-buttons')
    if (container) {
      const buttonsDiv = this.createButtonContainer(this.createEditButton(), this.createDeleteButton())
      container.appendChild(buttonsDiv)
    }
  }

  private renderEditView(): void {
    const urlTemplate = this.getAttribute('url-template') || ''
    const title = this.getAttribute('title') || ''
    const icon = this.getAttribute('icon') || '🔍'
    const placeholder = this.getAttribute('placeholder') || 'Enter query...'

    this.innerHTML = `
      <div class="widget-container query-widget widget-edit">
        <div class="widget-header">
          <h3 class="widget-title">Edit Query Widget</h3>
        </div>
        <div class="widget-content">
          <form class="widget-edit-form">
            <div class="form-group">
              <label for="query-url-template">URL Template:</label>
              <input
                type="text"
                id="query-url-template"
                name="url_template"
                value="${this.escapeHtml(urlTemplate)}"
                required
                placeholder="https://google.com/search?q={query}"
              />
              <small style="color: #666; font-size: 0.85rem;">Use {query} as placeholder for search term</small>
            </div>
            <div class="form-group">
              <label for="query-title">Title:</label>
              <input type="text" id="query-title" name="title" value="${this.escapeHtml(title)}" required />
            </div>
            <div class="form-group">
              <label for="query-icon">Icon (emoji or URL):</label>
              <div style="display: flex; gap: 0.5rem; align-items: center;">
                <input type="text" id="query-icon" name="icon" value="${this.escapeHtml(icon)}" required style="flex: 1;" />
                <button type="button" class="widget-btn refresh-favicon-btn" title="Refresh favicon from URL">
                  🔄
                </button>
              </div>
              <small style="color: #666; font-size: 0.85rem;">Leave as default to auto-fetch favicon</small>
            </div>
            <div class="form-group">
              <label for="query-placeholder">Placeholder Text:</label>
              <input type="text" id="query-placeholder" name="placeholder" value="${this.escapeHtml(placeholder)}" required />
            </div>
            <div class="form-buttons-container"></div>
          </form>
        </div>
      </div>
    `

    // Add refresh favicon button handler
    const refreshBtn = this.querySelector('.refresh-favicon-btn')
    if (refreshBtn) {
      refreshBtn.addEventListener('click', () => this.handleRefreshFavicon())
    }

    const container = this.querySelector('.form-buttons-container')
    if (container) {
      const buttonsDiv = this.createButtonContainer(this.createSaveButton(), this.createCancelButton())
      container.appendChild(buttonsDiv)
    }
  }

  protected extractPropertiesFromForm(): Record<string, unknown> {
    const form = this.querySelector('.widget-edit-form') as HTMLFormElement
    if (!form) {
      throw new Error('Form not found')
    }

    const formData = new FormData(form)
    const properties: QueryWidgetProperties = {
      url_template: formData.get('url_template') as string,
      title: formData.get('title') as string,
      icon: formData.get('icon') as string,
      placeholder: formData.get('placeholder') as string,
    }

    // Update attributes to reflect new values
    this.setAttribute('url-template', properties.url_template)
    this.setAttribute('title', properties.title)
    this.setAttribute('icon', properties.icon)
    this.setAttribute('placeholder', properties.placeholder)

    return properties as unknown as Record<string, unknown>
  }

  /**
   * Extract base URL from url_template for favicon fetching
   */
  private extractBaseUrl(urlTemplate: string): string | null {
    try {
      // Extract the base URL from the template (before the query parameter)
      // e.g., "https://google.com/search?q={query}" -> "https://google.com"
      const url = new URL(urlTemplate.replace('{query}', ''))
      return `${url.protocol}//${url.host}`
    } catch {
      return null
    }
  }

  /**
   * Render icon as either emoji text or img tag for data URLs
   */
  private renderIcon(icon: string): string {
    if (icon.startsWith('data:')) {
      // It's a data URL (favicon) - render as img
      return `<img src="${icon}" alt="favicon" class="favicon-img" />`
    } else if (icon.startsWith('http://') || icon.startsWith('https://')) {
      // It's an external URL - render as img
      return `<img src="${this.escapeHtml(icon)}" alt="icon" class="favicon-img" />`
    } else {
      // It's emoji or text - render as text
      return this.escapeHtml(icon)
    }
  }

  /**
   * Handle manual favicon refresh from edit form
   */
  private async handleRefreshFavicon(): Promise<void> {
    const urlTemplateInput = this.querySelector('#query-url-template') as HTMLInputElement
    const iconInput = this.querySelector('#query-icon') as HTMLInputElement
    const refreshBtn = this.querySelector('.refresh-favicon-btn') as HTMLButtonElement

    if (!urlTemplateInput || !iconInput || !refreshBtn) {
      return
    }

    const urlTemplate = urlTemplateInput.value.trim()
    if (!urlTemplate) {
      alert('Please enter a URL template first')
      return
    }

    const baseUrl = this.extractBaseUrl(urlTemplate)
    if (!baseUrl) {
      alert('Invalid URL template')
      return
    }

    // Disable button and show loading state
    refreshBtn.disabled = true
    refreshBtn.textContent = '⏳'

    try {
      const favicon = await this.fetchFavicon(baseUrl)
      if (favicon) {
        iconInput.value = favicon
        // Clear custom icon flag so it auto-updates
        localStorage.removeItem(`custom-icon-${baseUrl}`)
        alert('Favicon refreshed successfully!')
      } else {
        alert('No favicon found for this URL')
      }
    } catch (error) {
      console.error('Error refreshing favicon:', error)
      alert('Failed to refresh favicon')
    } finally {
      refreshBtn.disabled = false
      refreshBtn.textContent = '🔄'
    }
  }

  /**
   * Automatically fetch favicon for the widget's URL template
   */
  private async autoFetchFavicon(): Promise<void> {
    const urlTemplate = this.getAttribute('url-template')
    const currentIcon = this.getAttribute('icon')

    // Don't fetch if no URL template or already fetching
    if (!urlTemplate || this.isFetchingFavicon) {
      return
    }

    const baseUrl = this.extractBaseUrl(urlTemplate)
    if (!baseUrl) {
      return
    }

    // Don't fetch if user has set a custom icon (not the default emoji)
    const customIconKey = `custom-icon-${baseUrl}`
    if (currentIcon && currentIcon !== '🔍' && localStorage.getItem(customIconKey)) {
      return
    }

    // Check cache first
    if (this.faviconCache.has(baseUrl)) {
      const cachedFavicon = this.faviconCache.get(baseUrl)!
      this.updateIconDisplay(cachedFavicon)
      return
    }

    // Fetch from backend
    this.isFetchingFavicon = true
    try {
      const favicon = await this.fetchFavicon(baseUrl)
      if (favicon) {
        this.faviconCache.set(baseUrl, favicon)
        this.updateIconDisplay(favicon)
      }
    } catch (error) {
      console.warn('Failed to fetch favicon:', error)
    } finally {
      this.isFetchingFavicon = false
    }
  }

  /**
   * Fetch favicon from backend API
   */
  private async fetchFavicon(url: string): Promise<string | null> {
    try {
      const response = await fetch(`/api/favicon/?url=${encodeURIComponent(url)}`)
      if (!response.ok) {
        return null
      }

      const data = await response.json()
      if (data.success && data.favicon) {
        return data.favicon
      }

      return null
    } catch (error) {
      console.error('Error fetching favicon:', error)
      return null
    }
  }

  /**
   * Update the icon display with a favicon data URL or emoji
   */
  private updateIconDisplay(iconValue: string): void {
    const isDataUrl = iconValue.startsWith('data:')

    if (isDataUrl) {
      this.setAttribute('icon', iconValue)
      this.setAttribute('data-favicon-url', iconValue)
    } else {
      this.setAttribute('icon', iconValue)
    }

    this.render()
  }

  /**
   * Handle query form submission
   */
  private handleQuerySubmit(): void {
    const input = this.querySelector('.query-input') as HTMLInputElement
    if (!input) {
      return
    }

    const query = input.value.trim()
    if (!query) {
      return
    }

    const urlTemplate = this.getAttribute('url-template')
    if (!urlTemplate) {
      console.error('No URL template configured for query widget')
      return
    }

    // Replace {query} placeholder with URL-encoded query
    const encodedQuery = encodeURIComponent(query)
    const targetUrl = urlTemplate.replace('{query}', encodedQuery)

    // Open in new tab
    window.open(targetUrl, '_blank', 'noopener,noreferrer')

    // Clear input after submission
    input.value = ''
  }

  private escapeHtml(text: string): string {
    const div = document.createElement('div')
    div.textContent = text
    return div.innerHTML
  }
}

// Register custom element
customElements.define('query-widget', QueryWidget)
