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
                  <input type="text" id="shortcut-icon" name="shortcut_icon" value="🔗" />
                </div>
                <div class="form-group">
                  <label for="shortcut-description">Description:</label>
                  <textarea id="shortcut-description" name="shortcut_description" rows="3" placeholder="Optional"></textarea>
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
  }

  /**
   * Update which fields are visible based on selected type
   */
  private updateVisibleFields(): void {
    const iframeFields = this.querySelector('#iframe-fields') as HTMLElement
    const shortcutFields = this.querySelector('#shortcut-fields') as HTMLElement

    if (iframeFields && shortcutFields) {
      iframeFields.style.display = this.selectedType === WidgetType.IFRAME ? 'block' : 'none'
      shortcutFields.style.display = this.selectedType === WidgetType.SHORTCUT ? 'block' : 'none'

      // Update required attributes
      this.updateRequiredFields('iframe', this.selectedType === WidgetType.IFRAME)
      this.updateRequiredFields('shortcut', this.selectedType === WidgetType.SHORTCUT)
    }
  }

  /**
   * Update required attributes on fields
   */
  private updateRequiredFields(prefix: string, required: boolean): void {
    const urlField = this.querySelector(`#${prefix}-url`) as HTMLInputElement
    const titleField = this.querySelector(`#${prefix}-title`) as HTMLInputElement

    if (urlField) urlField.required = required
    if (titleField) titleField.required = required
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
    } else {
      properties = {
        url: formData.get('shortcut_url') as string,
        title: formData.get('shortcut_title') as string,
        icon: formData.get('shortcut_icon') as string,
        description: formData.get('shortcut_description') as string || null,
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
