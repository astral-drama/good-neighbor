/**
 * Iframe widget component
 * Embeds external content in an iframe
 */

import { BaseWidget } from './base-widget'
import type { IframeWidgetProperties } from '../types/widget'

export class IframeWidget extends BaseWidget {
  static get observedAttributes(): string[] {
    return ['url', 'title', 'width', 'height', 'refresh-interval']
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
    const title = this.getAttribute('title') || 'Iframe Widget'
    const width = this.getAttribute('width') || '400'
    const height = this.getAttribute('height') || '300'
    const inEditMode = this.isInEditMode()

    this.innerHTML = `
      <div class="widget-container iframe-widget">
        <div class="widget-header">
          <h3 class="widget-title">${this.escapeHtml(title)}</h3>
          ${inEditMode ? '<div class="widget-action-buttons"></div>' : ''}
        </div>
        <div class="widget-content">
          <iframe
            src="${this.escapeHtml(url)}"
            width="${width}"
            height="${height}"
            sandbox="allow-scripts allow-same-origin allow-forms allow-top-navigation allow-popups"
            loading="lazy"
            title="${this.escapeHtml(title)}"
          ></iframe>
        </div>
      </div>
    `

    // Add action buttons if in edit mode
    if (inEditMode) {
      const container = this.querySelector('.widget-action-buttons')
      if (container) {
        const buttonsDiv = this.createButtonContainer(this.createEditButton(), this.createDeleteButton())
        container.appendChild(buttonsDiv)
      }
    }

    // Set up auto-refresh if configured
    const refreshInterval = this.getAttribute('refresh-interval')
    if (refreshInterval) {
      const interval = parseInt(refreshInterval, 10) * 1000
      if (interval > 0) {
        setTimeout(() => this.refreshIframe(), interval)
      }
    }
  }

  private renderHoverView(): void {
    const url = this.getAttribute('url') || ''
    const title = this.getAttribute('title') || 'Iframe Widget'
    const width = this.getAttribute('width') || '400'
    const height = this.getAttribute('height') || '300'

    this.innerHTML = `
      <div class="widget-container iframe-widget widget-hover">
        <div class="widget-header">
          <h3 class="widget-title">${this.escapeHtml(title)}</h3>
          <div class="widget-action-buttons"></div>
        </div>
        <div class="widget-content">
          <iframe
            src="${this.escapeHtml(url)}"
            width="${width}"
            height="${height}"
            sandbox="allow-scripts allow-same-origin allow-forms allow-top-navigation allow-popups"
            loading="lazy"
            title="${this.escapeHtml(title)}"
          ></iframe>
        </div>
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
    const width = this.getAttribute('width') || '400'
    const height = this.getAttribute('height') || '300'
    const refreshInterval = this.getAttribute('refresh-interval') || ''

    this.innerHTML = `
      <div class="widget-container iframe-widget widget-edit">
        <div class="widget-header">
          <h3 class="widget-title">Edit Iframe Widget</h3>
        </div>
        <div class="widget-content">
          <form class="widget-edit-form">
            <div class="form-group">
              <label for="iframe-url">URL:</label>
              <input type="url" id="iframe-url" name="url" value="${this.escapeHtml(url)}" required />
            </div>
            <div class="form-group">
              <label for="iframe-title">Title:</label>
              <input type="text" id="iframe-title" name="title" value="${this.escapeHtml(title)}" required />
            </div>
            <div class="form-group">
              <label for="iframe-width">Width (px):</label>
              <input type="number" id="iframe-width" name="width" value="${width}" min="100" max="2000" required />
            </div>
            <div class="form-group">
              <label for="iframe-height">Height (px):</label>
              <input type="number" id="iframe-height" name="height" value="${height}" min="100" max="2000" required />
            </div>
            <div class="form-group">
              <label for="iframe-refresh">Refresh Interval (seconds):</label>
              <input type="number" id="iframe-refresh" name="refresh_interval" value="${refreshInterval}" min="5" placeholder="Optional" />
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
    const properties: IframeWidgetProperties = {
      url: formData.get('url') as string,
      title: formData.get('title') as string,
      width: parseInt(formData.get('width') as string, 10),
      height: parseInt(formData.get('height') as string, 10),
      refresh_interval: formData.get('refresh_interval')
        ? parseInt(formData.get('refresh_interval') as string, 10)
        : null,
    }

    // Update attributes to reflect new values
    this.setAttribute('url', properties.url)
    this.setAttribute('title', properties.title)
    this.setAttribute('width', properties.width.toString())
    this.setAttribute('height', properties.height.toString())
    if (properties.refresh_interval) {
      this.setAttribute('refresh-interval', properties.refresh_interval.toString())
    } else {
      this.removeAttribute('refresh-interval')
    }

    return properties as unknown as Record<string, unknown>
  }

  private refreshIframe(): void {
    const iframe = this.querySelector('iframe')
    if (iframe && this.state === 'normal' && iframe.src) {
      const currentSrc = iframe.src
      iframe.src = ''
      iframe.src = currentSrc // Reload iframe
    }
  }

  private escapeHtml(text: string): string {
    const div = document.createElement('div')
    div.textContent = text
    return div.innerHTML
  }
}

// Register custom element
customElements.define('iframe-widget', IframeWidget)
