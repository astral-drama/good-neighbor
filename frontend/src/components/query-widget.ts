/**
 * Query widget component
 * Allows users to submit text queries to configurable URLs
 */

import { BaseWidget } from './base-widget'
import type { QueryWidgetProperties } from '../types/widget'

export class QueryWidget extends BaseWidget {
  static get observedAttributes(): string[] {
    return ['url-template', 'title', 'icon', 'placeholder']
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

    this.innerHTML = `
      <div class="widget-container query-widget">
        <div class="query-header">
          <span class="query-icon">${this.escapeHtml(icon)}</span>
          <h3 class="query-title">${this.escapeHtml(title)}</h3>
        </div>
        <form class="query-form">
          <input
            type="text"
            class="query-input"
            placeholder="${this.escapeHtml(placeholder)}"
            autocomplete="off"
          />
          <button type="submit" class="query-submit-btn" title="Submit query">→</button>
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

    this.innerHTML = `
      <div class="widget-container query-widget widget-hover">
        <div class="widget-action-buttons"></div>
        <div class="query-header">
          <span class="query-icon">${this.escapeHtml(icon)}</span>
          <h3 class="query-title">${this.escapeHtml(title)}</h3>
        </div>
        <form class="query-form">
          <input
            type="text"
            class="query-input"
            placeholder="${this.escapeHtml(placeholder)}"
            autocomplete="off"
          />
          <button type="submit" class="query-submit-btn" title="Submit query">→</button>
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
              <label for="query-icon">Icon (emoji):</label>
              <input type="text" id="query-icon" name="icon" value="${this.escapeHtml(icon)}" required />
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
