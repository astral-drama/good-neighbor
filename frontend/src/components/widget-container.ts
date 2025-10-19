/**
 * WidgetContainer - A draggable container that groups widgets by type
 *
 * Features:
 * - Groups widgets of the same type
 * - Draggable via handle on the left side
 * - Displays drag handle on hover
 * - Emits events for reordering
 */

import { WidgetType } from '../types/widget';

export class WidgetContainer extends HTMLElement {
    private containerType: WidgetType;
    private widgets: HTMLElement[] = [];
    private dragHandle: HTMLElement | null = null;
    private contentArea: HTMLElement | null = null;

    constructor() {
        super();
        this.containerType = WidgetType.IFRAME;
    }

    connectedCallback() {
        const typeAttr = this.getAttribute('type');
        this.containerType = (typeAttr as WidgetType) || WidgetType.IFRAME;
        this.render();
        this.attachEventListeners();
    }

    private render() {
        this.className = 'widget-type-container';
        this.draggable = true;

        this.innerHTML = `
            <div class="container-wrapper">
                <div class="drag-handle" title="Drag to reorder">
                    <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                        <circle cx="7" cy="5" r="1.5"/>
                        <circle cx="13" cy="5" r="1.5"/>
                        <circle cx="7" cy="10" r="1.5"/>
                        <circle cx="13" cy="10" r="1.5"/>
                        <circle cx="7" cy="15" r="1.5"/>
                        <circle cx="13" cy="15" r="1.5"/>
                    </svg>
                </div>
                <div class="container-content">
                    <div class="container-header">
                        <h3>${this.getTypeDisplayName()}</h3>
                        <span class="widget-count">0 widgets</span>
                    </div>
                    <div class="container-widgets"></div>
                </div>
            </div>
        `;

        this.dragHandle = this.querySelector('.drag-handle');
        this.contentArea = this.querySelector('.container-widgets');
    }

    private getTypeDisplayName(): string {
        const displayNames: Record<WidgetType, string> = {
            [WidgetType.IFRAME]: 'Web Frames',
            [WidgetType.SHORTCUT]: 'Shortcuts'
        };
        return displayNames[this.containerType] || this.containerType;
    }

    private attachEventListeners() {
        // Drag handle mouse events for visual feedback
        if (this.dragHandle) {
            this.dragHandle.addEventListener('mouseenter', () => {
                this.classList.add('drag-handle-visible');
            });
        }

        this.addEventListener('mouseleave', () => {
            this.classList.remove('drag-handle-visible');
        });

        // Drag events
        this.addEventListener('dragstart', this.handleDragStart.bind(this));
        this.addEventListener('dragend', this.handleDragEnd.bind(this));
        this.addEventListener('dragover', this.handleDragOver.bind(this));
        this.addEventListener('drop', this.handleDrop.bind(this));
        this.addEventListener('dragenter', this.handleDragEnter.bind(this));
        this.addEventListener('dragleave', this.handleDragLeave.bind(this));
    }

    private handleDragStart(e: DragEvent) {
        if (!e.dataTransfer) return;

        this.classList.add('dragging');

        e.dataTransfer.effectAllowed = 'move';
        e.dataTransfer.setData('text/plain', this.containerType);
        e.dataTransfer.setData('container-type', this.containerType);

        // Create a custom drag image (optional)
        const dragImage = this.cloneNode(true) as HTMLElement;
        dragImage.style.opacity = '0.5';
        document.body.appendChild(dragImage);
        e.dataTransfer.setDragImage(dragImage, 0, 0);
        setTimeout(() => dragImage.remove(), 0);
    }

    private handleDragEnd() {
        this.classList.remove('dragging');
        this.classList.remove('drag-over');

        // Notify parent that drag ended
        this.dispatchEvent(new CustomEvent('container-drag-end', {
            bubbles: true,
            detail: { type: this.containerType }
        }));
    }

    private handleDragOver(e: DragEvent) {
        if (!e.dataTransfer) return;

        // Only allow drops from other containers
        if (e.dataTransfer.types.includes('container-type')) {
            e.preventDefault();
            e.dataTransfer.dropEffect = 'move';
        }
    }

    private handleDragEnter(e: DragEvent) {
        if (!e.dataTransfer) return;

        // Don't show drop zone on self
        const draggedType = e.dataTransfer.getData('container-type');
        if (draggedType && draggedType !== this.containerType) {
            this.classList.add('drag-over');
        }
    }

    private handleDragLeave(e: DragEvent) {
        // Only remove if actually leaving the container
        const rect = this.getBoundingClientRect();
        const x = e.clientX;
        const y = e.clientY;

        if (x < rect.left || x >= rect.right || y < rect.top || y >= rect.bottom) {
            this.classList.remove('drag-over');
        }
    }

    private handleDrop(e: DragEvent) {
        e.preventDefault();
        e.stopPropagation();

        if (!e.dataTransfer) return;

        const draggedType = e.dataTransfer.getData('container-type');

        if (draggedType && draggedType !== this.containerType) {
            this.classList.remove('drag-over');

            // Determine drop position (above or below)
            const rect = this.getBoundingClientRect();
            const midpoint = rect.top + rect.height / 2;
            const dropPosition = e.clientY < midpoint ? 'before' : 'after';

            // Dispatch event to parent to handle reordering
            this.dispatchEvent(new CustomEvent('container-reorder', {
                bubbles: true,
                detail: {
                    draggedType: draggedType,
                    targetType: this.containerType,
                    position: dropPosition
                }
            }));
        }
    }

    // Public API
    addWidget(widget: HTMLElement) {
        if (this.contentArea) {
            this.contentArea.appendChild(widget);
            this.widgets.push(widget);
            this.updateWidgetCount();
        }
    }

    removeWidget(widget: HTMLElement) {
        const index = this.widgets.indexOf(widget);
        if (index > -1) {
            this.widgets.splice(index, 1);
            widget.remove();
            this.updateWidgetCount();
        }
    }

    clearWidgets() {
        this.widgets = [];
        if (this.contentArea) {
            this.contentArea.innerHTML = '';
        }
        this.updateWidgetCount();
    }

    getWidgets(): HTMLElement[] {
        return [...this.widgets];
    }

    getType(): WidgetType {
        return this.containerType;
    }

    private updateWidgetCount() {
        const countElement = this.querySelector('.widget-count');
        if (countElement) {
            const count = this.widgets.length;
            countElement.textContent = `${count} widget${count !== 1 ? 's' : ''}`;
        }
    }

    isEmpty(): boolean {
        return this.widgets.length === 0;
    }
}

// Register the custom element
customElements.define('widget-container', WidgetContainer);
