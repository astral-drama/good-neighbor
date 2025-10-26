/**
 * Base widget component class
 * Provides shared functionality for all widget types
 */

import { deleteWidget, updateWidget } from '../services/widget-api'
import type { UpdateWidgetRequest } from '../types/widget'

export type WidgetState = 'normal' | 'hover' | 'edit'

export abstract class BaseWidget extends HTMLElement {
  protected state: WidgetState = 'normal'
  protected widgetId: string = ''
  private editModeObserver: MutationObserver | null = null

  connectedCallback(): void {
    this.widgetId = this.getAttribute('widget-id') || ''
    this.render()
    this.attachEventListeners()
    this.watchEditMode()
  }

  disconnectedCallback(): void {
    // Clean up observer when widget is removed
    if (this.editModeObserver) {
      this.editModeObserver.disconnect()
      this.editModeObserver = null
    }
  }

  /**
   * Watch for edit mode changes on the grid container
   */
  private watchEditMode(): void {
    const gridContainer = this.closest('.widget-grid-container')
    if (!gridContainer) {
      return
    }

    // Observe changes to the class attribute of the grid container
    this.editModeObserver = new MutationObserver(() => {
      // Re-render when edit mode changes (only in normal state)
      if (this.state === 'normal') {
        this.render()
      }
    })

    this.editModeObserver.observe(gridContainer, {
      attributes: true,
      attributeFilter: ['class'],
    })
  }

  /**
   * Render the widget based on current state
   * Must be implemented by subclasses
   */
  protected abstract render(): void

  /**
   * Check if the widget grid is in edit mode
   */
  protected isInEditMode(): boolean {
    const gridContainer = this.closest('.widget-grid-container')
    return gridContainer?.classList.contains('edit-mode') ?? false
  }

  /**
   * Attach event listeners for state management
   */
  protected attachEventListeners(): void {
    // Add hover listeners for state transitions
    // Only allow hover state if not in global edit mode
    this.addEventListener('mouseenter', () => {
      if (this.state === 'normal' && !this.isInEditMode()) {
        this.setState('hover')
      }
    })

    this.addEventListener('mouseleave', () => {
      if (this.state === 'hover') {
        this.setState('normal')
      }
    })
  }

  /**
   * Change widget state and re-render
   */
  protected setState(newState: WidgetState): void {
    this.state = newState
    this.render()
  }

  /**
   * Create a delete button for hover/edit views
   */
  protected createDeleteButton(): HTMLButtonElement {
    const btn = document.createElement('button')
    btn.type = 'button' // Prevent form submission
    btn.className = 'widget-btn widget-delete-btn'
    btn.textContent = '🗑️'
    btn.title = 'Delete widget'
    btn.onclick = (e) => {
      e.stopPropagation()
      void this.handleDelete()
    }
    return btn
  }

  /**
   * Create an edit button for hover view
   */
  protected createEditButton(): HTMLButtonElement {
    const btn = document.createElement('button')
    btn.type = 'button' // Prevent form submission
    btn.className = 'widget-btn widget-edit-btn'
    btn.textContent = '✏️'
    btn.title = 'Edit widget'
    btn.onclick = (e) => {
      e.stopPropagation()
      this.setState('edit')
    }
    return btn
  }

  /**
   * Create a save button for edit view
   */
  protected createSaveButton(): HTMLButtonElement {
    const btn = document.createElement('button')
    btn.type = 'button' // Prevent form submission
    btn.className = 'widget-btn widget-save-btn'
    btn.textContent = '💾'
    btn.title = 'Save changes'
    btn.onclick = (e) => {
      e.stopPropagation()
      void this.handleSave()
    }
    return btn
  }

  /**
   * Create a cancel button for edit view
   */
  protected createCancelButton(): HTMLButtonElement {
    const btn = document.createElement('button')
    btn.type = 'button' // Prevent form submission
    btn.className = 'widget-btn widget-cancel-btn'
    btn.textContent = '❌'
    btn.title = 'Cancel'
    btn.onclick = (e) => {
      e.stopPropagation()
      this.setState('normal')
    }
    return btn
  }

  /**
   * Handle widget deletion with confirmation
   */
  protected async handleDelete(): Promise<void> {
    const confirmed = confirm('Delete this widget?')
    if (!confirmed) {
      return
    }

    try {
      await deleteWidget(this.widgetId)
      // Dispatch custom event for widget grid to handle removal
      this.dispatchEvent(
        new CustomEvent('widget-deleted', {
          bubbles: true,
          detail: { widgetId: this.widgetId },
        }),
      )
      this.remove()
    } catch (error) {
      console.error('Failed to delete widget:', error)
      alert('Failed to delete widget. Please try again.')
    }
  }

  /**
   * Handle saving widget updates
   * Subclasses should override to extract and validate properties
   */
  protected async handleSave(): Promise<void> {
    try {
      const properties = this.extractPropertiesFromForm()
      const request: UpdateWidgetRequest = { properties }

      await updateWidget(this.widgetId, request)

      // Dispatch custom event for widget grid
      this.dispatchEvent(
        new CustomEvent('widget-updated', {
          bubbles: true,
          detail: { widgetId: this.widgetId, properties },
        }),
      )

      this.setState('normal')
    } catch (error) {
      console.error('Failed to save widget:', error)
      alert('Failed to save widget. Please try again.')
    }
  }

  /**
   * Extract properties from edit form
   * Must be implemented by subclasses
   */
  protected abstract extractPropertiesFromForm(): Record<string, unknown>

  /**
   * Create button container for widget controls
   */
  protected createButtonContainer(...buttons: HTMLButtonElement[]): HTMLDivElement {
    const container = document.createElement('div')
    container.className = 'widget-buttons'
    buttons.forEach((btn) => container.appendChild(btn))
    return container
  }
}
