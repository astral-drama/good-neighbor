/**
 * Homepage selector component
 * Allows users to switch between homepages and manage them
 */

import type { Homepage } from '../types/homepage'
import {
  listHomepages,
  createHomepage,
  updateHomepage,
  deleteHomepage,
  setDefaultHomepage,
} from '../services/homepage-api'

export class HomepageSelector extends HTMLElement {
  private homepages: Homepage[] = []
  private currentHomepage: Homepage | null = null
  private selectElement: HTMLSelectElement | null = null

  constructor() {
    super()
    this.innerHTML = this.template()
  }

  connectedCallback(): void {
    this.selectElement = this.querySelector('select')!
    this.setupEventListeners()
    void this.loadHomepages()
  }

  private template(): string {
    return `
      <div class="homepage-selector">
        <div class="selector-controls">
          <select class="homepage-select" aria-label="Select homepage">
            <option value="">Loading...</option>
          </select>
          <button class="manage-btn" title="Manage homepages" aria-label="Manage homepages">
            ⚙️
          </button>
        </div>
      </div>
    `
  }

  private setupEventListeners(): void {
    const select = this.querySelector('select')!
    const manageBtn = this.querySelector('.manage-btn')!

    select.addEventListener('change', () => {
      const selectedId = select.value
      const homepage = this.homepages.find(hp => hp.homepage_id === selectedId)
      if (homepage) {
        this.currentHomepage = homepage
        this.saveCurrentHomepageId(homepage.homepage_id)
        this.dispatchHomepageChanged(homepage)
      }
    })

    manageBtn.addEventListener('click', () => {
      this.openManageDialog()
    })
  }

  private async loadHomepages(): Promise<void> {
    try {
      this.homepages = await listHomepages()

      // If no homepages, create a default one
      if (this.homepages.length === 0) {
        const defaultHomepage = await createHomepage({ name: 'Home', is_default: true })
        this.homepages = [defaultHomepage]
      }

      this.renderSelect()

      // Load the saved homepage or use default
      const savedId = this.getSavedHomepageId()
      const homepage = savedId
        ? this.homepages.find(hp => hp.homepage_id === savedId)
        : this.homepages.find(hp => hp.is_default) || this.homepages[0]

      if (homepage) {
        this.currentHomepage = homepage
        this.selectElement!.value = homepage.homepage_id
        this.dispatchHomepageChanged(homepage)
      }
    } catch (error) {
      console.error('Failed to load homepages:', error)
      this.renderSelect()
    }
  }

  private renderSelect(): void {
    const select = this.selectElement!
    select.innerHTML = ''

    if (this.homepages.length === 0) {
      const option = document.createElement('option')
      option.value = ''
      option.textContent = 'No homepages'
      select.appendChild(option)
      return
    }

    this.homepages.forEach(homepage => {
      const option = document.createElement('option')
      option.value = homepage.homepage_id
      option.textContent = homepage.name + (homepage.is_default ? ' ⭐' : '')
      select.appendChild(option)
    })
  }

  private openManageDialog(): void {
    const dialog = document.createElement('dialog')
    dialog.className = 'homepage-manage-dialog'
    dialog.innerHTML = `
      <div class="dialog-header">
        <h2>Manage Homepages</h2>
        <button class="close-btn" aria-label="Close">×</button>
      </div>
      <div class="dialog-content">
        <div class="homepage-list">
          ${this.homepages.map(hp => `
            <div class="homepage-item" data-id="${hp.homepage_id}">
              <input
                type="text"
                value="${hp.name}"
                class="homepage-name"
                data-id="${hp.homepage_id}"
              />
              <button
                class="set-default-btn ${hp.is_default ? 'active' : ''}"
                data-id="${hp.homepage_id}"
                title="${hp.is_default ? 'Default' : 'Set as default'}"
                ${hp.is_default ? 'disabled' : ''}
              >
                ${hp.is_default ? '⭐' : '☆'}
              </button>
              <button
                class="delete-btn"
                data-id="${hp.homepage_id}"
                title="Delete homepage"
                ${this.homepages.length === 1 ? 'disabled' : ''}
              >
                🗑️
              </button>
            </div>
          `).join('')}
        </div>
        <button class="add-homepage-btn">+ New Homepage</button>
      </div>
    `

    document.body.appendChild(dialog)
    dialog.showModal()

    // Event listeners
    const closeBtn = dialog.querySelector('.close-btn')!
    closeBtn.addEventListener('click', () => {
      dialog.close()
      dialog.remove()
    })

    dialog.addEventListener('click', (e) => {
      if (e.target === dialog) {
        dialog.close()
        dialog.remove()
      }
    })

    // Handle homepage name updates
    dialog.querySelectorAll('.homepage-name').forEach(input => {
      const inputEl = input as HTMLInputElement
      inputEl.addEventListener('blur', () => {
        const id = inputEl.dataset.id!
        const newName = inputEl.value.trim()
        if (newName && newName !== this.homepages.find(hp => hp.homepage_id === id)?.name) {
          void (async () => {
            try {
              await updateHomepage(id, { name: newName })
              await this.loadHomepages()
            } catch (error) {
              console.error('Failed to update homepage:', error)
              alert('Failed to update homepage')
            }
          })()
        }
      })
    })

    // Handle set default
    dialog.querySelectorAll('.set-default-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const id = (btn as HTMLButtonElement).dataset.id!
        void (async () => {
          try {
            await setDefaultHomepage(id)
            await this.loadHomepages()
            dialog.close()
            dialog.remove()
            this.openManageDialog() // Reopen with updated data
          } catch (error) {
            console.error('Failed to set default homepage:', error)
            alert('Failed to set default homepage')
          }
        })()
      })
    })

    // Handle delete
    dialog.querySelectorAll('.delete-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const id = (btn as HTMLButtonElement).dataset.id!
        const homepage = this.homepages.find(hp => hp.homepage_id === id)
        if (!homepage) return

        if (!confirm(`Are you sure you want to delete "${homepage.name}"?`)) {
          return
        }

        void (async () => {
          try {
            await deleteHomepage(id)
            await this.loadHomepages()
            dialog.close()
            dialog.remove()
          } catch (error) {
            console.error('Failed to delete homepage:', error)
            alert('Failed to delete homepage. Cannot delete the last homepage.')
          }
        })()
      })
    })

    // Handle add new
    const addBtn = dialog.querySelector('.add-homepage-btn')!
    addBtn.addEventListener('click', () => {
      const name = prompt('Enter homepage name:')
      if (!name?.trim()) return

      void (async () => {
        try {
          await createHomepage({ name: name.trim(), is_default: false })
          await this.loadHomepages()
          dialog.close()
          dialog.remove()
          this.openManageDialog() // Reopen with updated data
        } catch (error) {
          console.error('Failed to create homepage:', error)
          alert('Failed to create homepage')
        }
      })()
    })
  }

  private dispatchHomepageChanged(homepage: Homepage): void {
    this.dispatchEvent(
      new CustomEvent('homepage-changed', {
        detail: { homepage },
        bubbles: true,
        composed: true,
      })
    )
  }

  private saveCurrentHomepageId(homepageId: string): void {
    localStorage.setItem('good-neighbor-current-homepage', homepageId)
  }

  private getSavedHomepageId(): string | null {
    return localStorage.getItem('good-neighbor-current-homepage')
  }

  getCurrentHomepage(): Homepage | null {
    return this.currentHomepage
  }

  async refresh(): Promise<void> {
    await this.loadHomepages()
  }
}

customElements.define('homepage-selector', HomepageSelector)
