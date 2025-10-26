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
    this.setupDragAndDrop()
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
      const inEditMode = this.isInEditMode()
      // Set draggable attribute based on edit mode
      this.draggable = inEditMode && this.state === 'normal'

      // Re-render when edit mode changes (only in normal state)
      if (this.state === 'normal') {
        this.render()
      }
    })

    this.editModeObserver.observe(gridContainer, {
      attributes: true,
      attributeFilter: ['class'],
    })

    // Set initial draggable state
    this.draggable = this.isInEditMode() && this.state === 'normal'
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
    // No hover listeners - edit buttons only show in edit mode
    // Hover state is no longer used for showing edit buttons
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

  /**
   * Setup drag-and-drop for reordering widgets within containers
   */
  private setupDragAndDrop(): void {
    // Make widget draggable when in edit mode
    this.addEventListener('dragstart', this.handleDragStart.bind(this))
    this.addEventListener('dragend', this.handleDragEnd.bind(this))
    this.addEventListener('dragover', this.handleDragOver.bind(this))
    this.addEventListener('drop', this.handleDrop.bind(this))
    this.addEventListener('dragenter', this.handleDragEnter.bind(this))
    this.addEventListener('dragleave', this.handleDragLeave.bind(this))
  }

  private handleDragStart(e: DragEvent): void {
    // Only allow dragging in edit mode and normal state
    if (!this.isInEditMode() || this.state !== 'normal') {
      e.preventDefault()
      return
    }

    if (!e.dataTransfer) return

    this.classList.add('dragging-widget')
    e.dataTransfer.effectAllowed = 'move'
    e.dataTransfer.setData('widget-id', this.widgetId)
  }

  private handleDragEnd(): void {
    this.classList.remove('dragging-widget')
    this.classList.remove('drag-over-widget')
  }

  private handleDragOver(e: DragEvent): void {
    if (!this.isInEditMode()) return
    if (!e.dataTransfer || !e.dataTransfer.types.includes('widget-id')) return

    e.preventDefault()
    e.dataTransfer.dropEffect = 'move'
  }

  private handleDragEnter(e: DragEvent): void {
    if (!this.isInEditMode()) return
    if (!e.dataTransfer || !e.dataTransfer.types.includes('widget-id')) return

    const draggedWidgetId = e.dataTransfer.getData('widget-id')
    if (draggedWidgetId && draggedWidgetId !== this.widgetId) {
      this.classList.add('drag-over-widget')
    }
  }

  private handleDragLeave(e: DragEvent): void {
    // Only remove if actually leaving the widget
    const rect = this.getBoundingClientRect()
    const x = e.clientX
    const y = e.clientY

    if (x < rect.left || x >= rect.right || y < rect.top || y >= rect.bottom) {
      this.classList.remove('drag-over-widget')
    }
  }

  private handleDrop(e: DragEvent): void {
    if (!this.isInEditMode()) return
    if (!e.dataTransfer) return

    e.preventDefault()
    e.stopPropagation()

    const draggedWidgetId = e.dataTransfer.getData('widget-id')
    if (!draggedWidgetId || draggedWidgetId === this.widgetId) {
      this.classList.remove('drag-over-widget')
      return
    }

    this.classList.remove('drag-over-widget')

    // Determine drop position (above or below)
    const rect = this.getBoundingClientRect()
    const midpoint = rect.top + rect.height / 2
    const dropPosition = e.clientY < midpoint ? 'before' : 'after'

    // Dispatch event for widget grid to handle reordering
    this.dispatchEvent(
      new CustomEvent('widget-reorder', {
        bubbles: true,
        detail: {
          draggedWidgetId,
          targetWidgetId: this.widgetId,
          position: dropPosition,
        },
      })
    )
  }
}
