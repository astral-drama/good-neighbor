/**
 * WidgetContainer - A draggable container that groups widgets by type
 * Uses SortableJS for reliable drag-and-drop functionality
 */

import Sortable from 'sortablejs';
import { WidgetType } from '../types/widget';

export class WidgetContainer extends HTMLElement {
    private containerType: WidgetType;
    private widgets: HTMLElement[] = [];
    private contentArea: HTMLElement | null = null;
    private sortableInstance: Sortable | null = null;
    private editModeObserver: MutationObserver | null = null;

    constructor() {
        super();
        this.containerType = WidgetType.IFRAME;
    }

    connectedCallback() {
        const typeAttr = this.getAttribute('type');
        this.containerType = (typeAttr as WidgetType) || WidgetType.IFRAME;
        this.render();
        this.watchEditMode();
    }

    disconnectedCallback() {
        // Clean up Sortable instance
        if (this.sortableInstance) {
            this.sortableInstance.destroy();
            this.sortableInstance = null;
        }
        // Clean up observer
        if (this.editModeObserver) {
            this.editModeObserver.disconnect();
            this.editModeObserver = null;
        }
    }

    private render() {
        this.className = 'widget-type-container';
        this.setAttribute('type', this.containerType);

        this.innerHTML = `
            <div class="container-wrapper">
                <div class="drag-handle" title="Drag to reorder sections">
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

        this.contentArea = this.querySelector('.container-widgets');

        // Initialize Sortable based on current edit mode
        this.updateSortable();
    }

    private getTypeDisplayName(): string {
        const displayNames: Record<WidgetType, string> = {
            [WidgetType.IFRAME]: 'Web Frames',
            [WidgetType.SHORTCUT]: 'Shortcuts',
            [WidgetType.QUERY]: 'Search'
        };
        return displayNames[this.containerType] || this.containerType;
    }

    /**
     * Watch for edit mode changes on the grid container
     */
    private watchEditMode(): void {
        const gridContainer = this.closest('.widget-grid-container');
        if (!gridContainer) {
            return;
        }

        this.editModeObserver = new MutationObserver(() => {
            this.updateSortable();
        });

        this.editModeObserver.observe(gridContainer, {
            attributes: true,
            attributeFilter: ['class'],
        });
    }

    /**
     * Check if we're in edit mode
     */
    private isInEditMode(): boolean {
        const gridContainer = this.closest('.widget-grid-container');
        return gridContainer?.classList.contains('edit-mode') ?? false;
    }

    /**
     * Initialize or update Sortable based on edit mode
     */
    private updateSortable(): void {
        if (!this.contentArea) return;

        const inEditMode = this.isInEditMode();

        if (inEditMode && !this.sortableInstance) {
            // Initialize Sortable for widget reordering
            this.sortableInstance = Sortable.create(this.contentArea, {
                animation: 150,
                easing: 'cubic-bezier(1, 0, 0, 1)',
                ghostClass: 'sortable-ghost',
                chosenClass: 'sortable-chosen',
                dragClass: 'sortable-drag',
                // Only allow sorting within the same container type
                group: {
                    name: `widgets-${this.containerType}`,
                    pull: false,
                    put: false
                },
                onEnd: (evt) => {
                    this.handleSortEnd(evt);
                }
            });
        } else if (!inEditMode && this.sortableInstance) {
            // Destroy Sortable when exiting edit mode
            this.sortableInstance.destroy();
            this.sortableInstance = null;
        } else if (inEditMode && this.sortableInstance) {
            // Update disabled state
            this.sortableInstance.option('disabled', false);
        }
    }

    /**
     * Handle the end of a sort operation
     */
    private handleSortEnd(evt: Sortable.SortableEvent): void {
        const { oldIndex, newIndex } = evt;

        if (oldIndex === undefined || newIndex === undefined || oldIndex === newIndex) {
            return;
        }

        // Get widget IDs in new order
        const widgetElements = this.contentArea?.querySelectorAll('[widget-id]');
        if (!widgetElements) return;

        const widgetIds = Array.from(widgetElements).map(el => el.getAttribute('widget-id'));

        // Dispatch event for widget-grid to handle the reorder
        this.dispatchEvent(new CustomEvent('widgets-reordered', {
            bubbles: true,
            detail: {
                containerType: this.containerType,
                widgetIds: widgetIds,
                oldIndex,
                newIndex
            }
        }));
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
