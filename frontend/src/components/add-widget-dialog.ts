/**
 * Add widget dialog component
 * Modal dialog for creating new widgets
 */

import { createWidget } from '../services/widget-api'
import type { CreateWidgetRequest, Widget } from '../types/widget'
import { WidgetType } from '../types/widget'

export class AddWidgetDialog extends HTMLElement {
  private isOpen: boolean = false
  private selectedType: WidgetType | null = null

  connectedCallback(): void {
    this.render()
    this.attachEventListeners()
  }

  /**
   * Open the dialog
   */
  public open(): void {
    this.isOpen = true
    this.selectedType = null
    this.render()
  }

  /**
   * Close the dialog
   */
  public close(): void {
    this.isOpen = false
    this.render()
  }

  /**
   * Render the dialog
   */
  private render(): void {
    if (!this.isOpen) {
      this.innerHTML = ''
      return
    }

    this.innerHTML = `
      <div class="dialog-overlay">
        <div class="dialog-container">
          <div class="dialog-header">
            <h2>Add New Widget</h2>
            <button class="dialog-close-btn" title="Close">&times;</button>
          </div>
          <div class="dialog-content">
            <form class="add-widget-form">
              <div class="form-group">
                <label for="widget-type">Widget Type:</label>
                <select id="widget-type" name="type" required>
                  <option value="">Select a type...</option>
                  <option value="iframe">Iframe Widget</option>
                  <option value="shortcut">Shortcut Widget</option>
                  <option value="query">Query Widget</option>
                </select>
              </div>

              <div id="iframe-fields" class="type-specific-fields" style="display: none;">
                <div class="form-group">
                  <label for="iframe-url">URL:</label>
                  <input type="url" id="iframe-url" name="iframe_url" placeholder="https://example.com" />
                </div>
                <div class="form-group">
                  <label for="iframe-title">Title:</label>
                  <input type="text" id="iframe-title" name="iframe_title" placeholder="My Iframe" />
                </div>
                <div class="form-group">
                  <label for="iframe-width">Width (px):</label>
                  <input type="number" id="iframe-width" name="iframe_width" value="400" min="100" max="2000" />
                </div>
                <div class="form-group">
                  <label for="iframe-height">Height (px):</label>
                  <input type="number" id="iframe-height" name="iframe_height" value="300" min="100" max="2000" />
                </div>
                <div class="form-group">
                  <label for="iframe-refresh">Refresh Interval (seconds):</label>
                  <input type="number" id="iframe-refresh" name="iframe_refresh" min="5" placeholder="Optional" />
                </div>
              </div>

              <div id="shortcut-fields" class="type-specific-fields" style="display: none;">
                <div class="form-group">
                  <label for="shortcut-url">URL:</label>
                  <input type="url" id="shortcut-url" name="shortcut_url" placeholder="https://example.com" />
                </div>
                <div class="form-group">
                  <label for="shortcut-title">Title:</label>
                  <input type="text" id="shortcut-title" name="shortcut_title" placeholder="My Shortcut" />
                </div>
                <div class="form-group">
                  <label for="shortcut-icon">Icon (emoji or URL):</label>
                  <div style="display: flex; gap: 0.5rem; align-items: flex-start;">
                    <div style="flex: 1;">
                      <input type="text" id="shortcut-icon" name="shortcut_icon" value="🔗" />
                      <small style="display: block; color: #666; font-size: 0.85rem; margin-top: 0.25rem;">
                        Leave as 🔗 to auto-fetch favicon, or enter custom emoji/URL
                      </small>
                    </div>
                    <button type="button" class="widget-btn fetch-favicon-btn" title="Fetch favicon from URL">
                      🔍 Fetch
                    </button>
                  </div>
                  <div class="favicon-preview" style="display: none; margin-top: 0.5rem; padding: 0.5rem; background: rgba(255,255,255,0.05); border-radius: 4px;">
                    <small style="color: #888;">Preview:</small>
                    <div class="favicon-preview-icon" style="margin-top: 0.25rem;"></div>
                  </div>
                </div>
                <div class="form-group">
                  <label for="shortcut-description">Description:</label>
                  <textarea id="shortcut-description" name="shortcut_description" rows="3" placeholder="Optional"></textarea>
                </div>
              </div>

              <div id="query-fields" class="type-specific-fields" style="display: none;">
                <div class="form-group">
                  <label for="query-url-template">URL Template:</label>
                  <input type="text" id="query-url-template" name="query_url_template" placeholder="https://google.com/search?q={query}" />
                  <small style="display: block; color: #666; font-size: 0.85rem; margin-top: 0.25rem;">
                    Use {query} as placeholder for the search term
                  </small>
                </div>
                <div class="form-group">
                  <label for="query-title">Title:</label>
                  <input type="text" id="query-title" name="query_title" placeholder="Search" />
                </div>
                <div class="form-group">
                  <label for="query-icon">Icon (emoji):</label>
                  <input type="text" id="query-icon" name="query_icon" value="🔍" />
                </div>
                <div class="form-group">
                  <label for="query-placeholder">Placeholder Text:</label>
                  <input type="text" id="query-placeholder" name="query_placeholder" value="Enter query..." />
                </div>
              </div>

              <div class="dialog-actions">
                <button type="button" class="btn btn-cancel">Cancel</button>
                <button type="submit" class="btn btn-primary">Create Widget</button>
              </div>
            </form>
          </div>
        </div>
      </div>
    `
  }

  /**
   * Attach event listeners
   */
  private attachEventListeners(): void {
    // Close button
    this.addEventListener('click', (event) => {
      const target = event.target as HTMLElement
      if (target.classList.contains('dialog-close-btn') || target.classList.contains('btn-cancel')) {
        this.close()
      }
    })

    // Close on overlay click
    this.addEventListener('click', (event) => {
      const target = event.target as HTMLElement
      if (target.classList.contains('dialog-overlay')) {
        this.close()
      }
    })

    // Widget type selection
    this.addEventListener('change', (event) => {
      const target = event.target as HTMLSelectElement
      if (target.id === 'widget-type') {
        this.selectedType = target.value as WidgetType
        this.updateVisibleFields()
      }
    })

    // Form submission
    this.addEventListener('submit', (event) => {
      event.preventDefault()
      void this.handleSubmit()
    })

    // Fetch favicon button
    this.addEventListener('click', (event) => {
      const target = event.target as HTMLElement
      if (target.classList.contains('fetch-favicon-btn')) {
        void this.handleFetchFavicon()
      }
    })
  }

  /**
   * Update which fields are visible based on selected type
   */
  private updateVisibleFields(): void {
    const iframeFields = this.querySelector('#iframe-fields') as HTMLElement
    const shortcutFields = this.querySelector('#shortcut-fields') as HTMLElement
    const queryFields = this.querySelector('#query-fields') as HTMLElement

    if (iframeFields && shortcutFields && queryFields) {
      iframeFields.style.display = this.selectedType === WidgetType.IFRAME ? 'block' : 'none'
      shortcutFields.style.display = this.selectedType === WidgetType.SHORTCUT ? 'block' : 'none'
      queryFields.style.display = this.selectedType === WidgetType.QUERY ? 'block' : 'none'

      // Update required attributes
      this.updateRequiredFields('iframe', this.selectedType === WidgetType.IFRAME)
      this.updateRequiredFields('shortcut', this.selectedType === WidgetType.SHORTCUT)
      this.updateRequiredFields('query', this.selectedType === WidgetType.QUERY)
    }
  }

  /**
   * Update required attributes on fields
   */
  private updateRequiredFields(prefix: string, required: boolean): void {
    if (prefix === 'query') {
      const urlTemplateField = this.querySelector('#query-url-template') as HTMLInputElement
      const titleField = this.querySelector('#query-title') as HTMLInputElement
      if (urlTemplateField) urlTemplateField.required = required
      if (titleField) titleField.required = required
    } else {
      const urlField = this.querySelector(`#${prefix}-url`) as HTMLInputElement
      const titleField = this.querySelector(`#${prefix}-title`) as HTMLInputElement
      if (urlField) urlField.required = required
      if (titleField) titleField.required = required
    }
  }

  /**
   * Handle favicon fetch button click
   */
  private async handleFetchFavicon(): Promise<void> {
    const urlInput = this.querySelector('#shortcut-url') as HTMLInputElement
    const iconInput = this.querySelector('#shortcut-icon') as HTMLInputElement
    const fetchBtn = this.querySelector('.fetch-favicon-btn') as HTMLButtonElement
    const previewContainer = this.querySelector('.favicon-preview') as HTMLElement
    const previewIcon = this.querySelector('.favicon-preview-icon') as HTMLElement

    if (!urlInput || !iconInput || !fetchBtn || !previewContainer || !previewIcon) {
      return
    }

    const url = urlInput.value.trim()
    if (!url) {
      alert('Please enter a URL first')
      return
    }

    // Disable button and show loading state
    fetchBtn.disabled = true
    const originalText = fetchBtn.textContent
    fetchBtn.textContent = '⏳ Fetching...'

    try {
      const response = await fetch(`/api/favicon/?url=${encodeURIComponent(url)}`)
      if (!response.ok) {
        throw new Error('Failed to fetch favicon')
      }

      const data = await response.json()
      if (data.success && data.favicon) {
        // Update icon input with favicon data URL
        iconInput.value = data.favicon

        // Show preview
        if (data.favicon.startsWith('data:')) {
          previewIcon.innerHTML = `<img src="${data.favicon}" alt="favicon" style="width: 48px; height: 48px; object-fit: contain; border-radius: 4px;" />`
        } else {
          previewIcon.innerHTML = `<span style="font-size: 2rem;">${data.favicon}</span>`
        }
        previewContainer.style.display = 'block'

        // Show success message
        alert(`Favicon fetched successfully from ${data.source}!`)
      } else {
        alert('No favicon found for this URL. Using default icon.')
      }
    } catch (error) {
      console.error('Error fetching favicon:', error)
      alert('Failed to fetch favicon. Please try again or enter a custom icon.')
    } finally {
      fetchBtn.disabled = false
      fetchBtn.textContent = originalText
    }
  }

  /**
   * Handle form submission
   */
  private async handleSubmit(): Promise<void> {
    const form = this.querySelector('.add-widget-form') as HTMLFormElement
    if (!form || !this.selectedType) {
      return
    }

    const formData = new FormData(form)
    let properties: Record<string, unknown>

    if (this.selectedType === WidgetType.IFRAME) {
      properties = {
        url: formData.get('iframe_url') as string,
        title: formData.get('iframe_title') as string,
        width: parseInt(formData.get('iframe_width') as string, 10),
        height: parseInt(formData.get('iframe_height') as string, 10),
        refresh_interval: formData.get('iframe_refresh')
          ? parseInt(formData.get('iframe_refresh') as string, 10)
          : null,
      }
    } else if (this.selectedType === WidgetType.SHORTCUT) {
      properties = {
        url: formData.get('shortcut_url') as string,
        title: formData.get('shortcut_title') as string,
        icon: formData.get('shortcut_icon') as string,
        description: formData.get('shortcut_description') as string || null,
      }
    } else {
      properties = {
        url_template: formData.get('query_url_template') as string,
        title: formData.get('query_title') as string,
        icon: formData.get('query_icon') as string,
        placeholder: formData.get('query_placeholder') as string,
      }
    }

    const request: CreateWidgetRequest = {
      type: this.selectedType,
      properties,
    }

    try {
      const widget: Widget = await createWidget(request)

      // Dispatch event to notify grid
      this.dispatchEvent(
        new CustomEvent('widget-created', {
          bubbles: true,
          detail: { widget },
        })
      )

      this.close()
    } catch (error) {
      console.error('Failed to create widget:', error)
      alert('Failed to create widget. Please try again.')
    }
  }
}

// Register custom element
customElements.define('add-widget-dialog', AddWidgetDialog)
