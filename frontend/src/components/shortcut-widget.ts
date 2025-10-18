/**
 * Shortcut widget component
 * Displays a clickable link with icon and description
 */

import { BaseWidget } from './base-widget'
import type { ShortcutWidgetProperties } from '../types/widget'

export class ShortcutWidget extends BaseWidget {
  static get observedAttributes(): string[] {
    return ['url', 'title', 'icon', 'description']
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

    this.innerHTML = `
      <div class="widget-container shortcut-widget">
        <a href="${this.escapeHtml(url)}" class="shortcut-link" target="_blank" rel="noopener noreferrer">
          <div class="shortcut-icon">${this.escapeHtml(icon)}</div>
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

    this.innerHTML = `
      <div class="widget-container shortcut-widget widget-hover">
        <div class="widget-action-buttons"></div>
        <a href="${this.escapeHtml(url)}" class="shortcut-link" target="_blank" rel="noopener noreferrer">
          <div class="shortcut-icon">${this.escapeHtml(icon)}</div>
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
              <input type="text" id="shortcut-icon" name="icon" value="${this.escapeHtml(icon)}" required />
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
}

// Register custom element
customElements.define('shortcut-widget', ShortcutWidget)
