/**
 * Shortcut widget component
 * Displays a clickable link with icon and description
 */

import { BaseWidget } from './base-widget'
import type { ShortcutWidgetProperties } from '../types/widget'

export class ShortcutWidget extends BaseWidget {
  private faviconCache: Map<string, string> = new Map()
  private isFetchingFavicon = false

  static get observedAttributes(): string[] {
    return ['url', 'title', 'icon', 'description']
  }

  connectedCallback(): void {
    super.connectedCallback()
    this.autoFetchFavicon()
  }

  attributeChangedCallback(name: string, oldValue: string | null, newValue: string | null): void {
    // Auto-fetch favicon when URL changes
    if (name === 'url' && oldValue !== newValue) {
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
    const url = this.getAttribute('url') || ''
    const title = this.getAttribute('title') || 'Shortcut'
    const icon = this.getAttribute('icon') || '🔗'
    const description = this.getAttribute('description') || ''

    const iconHtml = this.renderIcon(icon)

    this.innerHTML = `
      <div class="widget-container shortcut-widget">
        <a href="${this.escapeHtml(url)}" class="shortcut-link">
          <div class="shortcut-icon">${iconHtml}</div>
          <div class="shortcut-content">
            <h3 class="shortcut-title">${this.escapeHtml(title)}</h3>
            ${description ? `<p class="shortcut-description">${this.escapeHtml(description)}</p>` : ''}
          </div>
        </a>
      </div>
    `
  }

  private renderHoverView(): void {
    const url = this.getAttribute('url') || ''
    const title = this.getAttribute('title') || 'Shortcut'
    const icon = this.getAttribute('icon') || '🔗'
    const description = this.getAttribute('description') || ''

    const iconHtml = this.renderIcon(icon)

    this.innerHTML = `
      <div class="widget-container shortcut-widget widget-hover">
        <div class="widget-action-buttons"></div>
        <a href="${this.escapeHtml(url)}" class="shortcut-link">
          <div class="shortcut-icon">${iconHtml}</div>
          <div class="shortcut-content">
            <h3 class="shortcut-title">${this.escapeHtml(title)}</h3>
            ${description ? `<p class="shortcut-description">${this.escapeHtml(description)}</p>` : ''}
          </div>
        </a>
      </div>
    `

    const container = this.querySelector('.widget-action-buttons')
    if (container) {
      const buttonsDiv = this.createButtonContainer(this.createEditButton(), this.createDeleteButton())
      container.appendChild(buttonsDiv)
    }
  }

  private renderEditView(): void {
    const url = this.getAttribute('url') || ''
    const title = this.getAttribute('title') || ''
    const icon = this.getAttribute('icon') || '🔗'
    const description = this.getAttribute('description') || ''

    this.innerHTML = `
      <div class="widget-container shortcut-widget widget-edit">
        <div class="widget-header">
          <h3 class="widget-title">Edit Shortcut Widget</h3>
        </div>
        <div class="widget-content">
          <form class="widget-edit-form">
            <div class="form-group">
              <label for="shortcut-url">URL:</label>
              <input type="url" id="shortcut-url" name="url" value="${this.escapeHtml(url)}" required />
            </div>
            <div class="form-group">
              <label for="shortcut-title">Title:</label>
              <input type="text" id="shortcut-title" name="title" value="${this.escapeHtml(title)}" required />
            </div>
            <div class="form-group">
              <label for="shortcut-icon">Icon (emoji or URL):</label>
              <div style="display: flex; gap: 0.5rem; align-items: center;">
                <input type="text" id="shortcut-icon" name="icon" value="${this.escapeHtml(icon)}" required style="flex: 1;" />
                <button type="button" class="widget-btn refresh-favicon-btn" title="Refresh favicon from URL">
                  🔄
                </button>
              </div>
              <small style="color: #666; font-size: 0.85rem;">Leave as default to auto-fetch favicon</small>
            </div>
            <div class="form-group">
              <label for="shortcut-description">Description:</label>
              <textarea id="shortcut-description" name="description" rows="3" placeholder="Optional">${this.escapeHtml(description)}</textarea>
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
    const properties: ShortcutWidgetProperties = {
      url: formData.get('url') as string,
      title: formData.get('title') as string,
      icon: formData.get('icon') as string,
      description: formData.get('description') as string || null,
    }

    // Update attributes to reflect new values
    this.setAttribute('url', properties.url)
    this.setAttribute('title', properties.title)
    this.setAttribute('icon', properties.icon)
    if (properties.description) {
      this.setAttribute('description', properties.description)
    } else {
      this.removeAttribute('description')
    }

    return properties as unknown as Record<string, unknown>
  }

  private escapeHtml(text: string): string {
    const div = document.createElement('div')
    div.textContent = text
    return div.innerHTML
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
    const urlInput = this.querySelector('#shortcut-url') as HTMLInputElement
    const iconInput = this.querySelector('#shortcut-icon') as HTMLInputElement
    const refreshBtn = this.querySelector('.refresh-favicon-btn') as HTMLButtonElement

    if (!urlInput || !iconInput || !refreshBtn) {
      return
    }

    const url = urlInput.value.trim()
    if (!url) {
      alert('Please enter a URL first')
      return
    }

    // Disable button and show loading state
    refreshBtn.disabled = true
    refreshBtn.textContent = '⏳'

    try {
      const favicon = await this.fetchFavicon(url)
      if (favicon) {
        iconInput.value = favicon
        // Clear custom icon flag so it auto-updates
        localStorage.removeItem(`custom-icon-${url}`)
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
   * Automatically fetch favicon for the widget's URL
   * Only fetches if icon is not already set to a custom value
   */
  private async autoFetchFavicon(): Promise<void> {
    const url = this.getAttribute('url')
    const currentIcon = this.getAttribute('icon')

    // Don't fetch if no URL or already fetching
    if (!url || this.isFetchingFavicon) {
      return
    }

    // Don't fetch if user has set a custom icon (not the default emoji)
    // We check localStorage to see if this URL has been customized
    const customIconKey = `custom-icon-${url}`
    if (currentIcon && currentIcon !== '🔗' && localStorage.getItem(customIconKey)) {
      return
    }

    // Check cache first
    if (this.faviconCache.has(url)) {
      const cachedFavicon = this.faviconCache.get(url)!
      this.updateIconDisplay(cachedFavicon)
      return
    }

    // Fetch from backend
    this.isFetchingFavicon = true
    try {
      const favicon = await this.fetchFavicon(url)
      if (favicon) {
        this.faviconCache.set(url, favicon)
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
      const baseUrl = import.meta.env.BASE_URL.replace(/\/$/, '')
      const response = await fetch(`${baseUrl}/api/favicon/?url=${encodeURIComponent(url)}`)
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
    // Check if it's a data URL (favicon) or emoji
    const isDataUrl = iconValue.startsWith('data:')

    if (isDataUrl) {
      // For data URLs, we need to update the icon rendering to use an img tag
      this.setAttribute('icon', iconValue)
      this.setAttribute('data-favicon-url', iconValue)
    } else {
      this.setAttribute('icon', iconValue)
    }

    this.render()
  }
}

// Register custom element
customElements.define('shortcut-widget', ShortcutWidget)
