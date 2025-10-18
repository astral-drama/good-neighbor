import { describe, it, expect, beforeEach } from 'vitest'
import { ShortcutWidget } from './shortcut-widget'

describe('ShortcutWidget', () => {
  beforeEach(() => {
    document.body.innerHTML = '<div id="test-container"></div>'
  })

  it('should render shortcut link with icon and title', () => {
    const widget = new ShortcutWidget()
    widget.setAttribute('widget-id', 'test-123')
    widget.setAttribute('url', 'https://example.com')
    widget.setAttribute('title', 'Example Site')
    widget.setAttribute('icon', '🌐')
    document.body.appendChild(widget)

    const link = widget.querySelector('.shortcut-link') as HTMLAnchorElement
    expect(link).toBeTruthy()
    expect(link?.getAttribute('href')).toContain('example.com')
    expect(link?.getAttribute('target')).toBe('_blank')
    expect(link?.getAttribute('rel')).toBe('noopener noreferrer')

    const icon = widget.querySelector('.shortcut-icon')
    expect(icon?.textContent).toBe('🌐')

    const title = widget.querySelector('.shortcut-title')
    expect(title?.textContent).toBe('Example Site')
  })

  it('should render description when provided', () => {
    const widget = new ShortcutWidget()
    widget.setAttribute('widget-id', 'test-123')
    widget.setAttribute('url', 'https://example.com')
    widget.setAttribute('title', 'Example')
    widget.setAttribute('description', 'This is a test description')
    document.body.appendChild(widget)

    const description = widget.querySelector('.shortcut-description')
    expect(description).toBeTruthy()
    expect(description?.textContent).toBe('This is a test description')
  })

  it('should not render description element when not provided', () => {
    const widget = new ShortcutWidget()
    widget.setAttribute('widget-id', 'test-123')
    widget.setAttribute('url', 'https://example.com')
    widget.setAttribute('title', 'Example')
    document.body.appendChild(widget)

    const description = widget.querySelector('.shortcut-description')
    expect(description).toBeFalsy()
  })

  it('should use default icon when not provided', () => {
    const widget = new ShortcutWidget()
    widget.setAttribute('widget-id', 'test-123')
    widget.setAttribute('url', 'https://example.com')
    widget.setAttribute('title', 'Example')
    document.body.appendChild(widget)

    const icon = widget.querySelector('.shortcut-icon')
    expect(icon?.textContent).toBe('🔗')
  })

  it('should escape HTML in attributes', () => {
    const widget = new ShortcutWidget()
    widget.setAttribute('widget-id', 'test-123')
    widget.setAttribute('title', '<script>alert("xss")</script>')
    widget.setAttribute('url', 'javascript:alert("xss")')
    widget.setAttribute('description', '<img src=x onerror=alert(1)>')
    document.body.appendChild(widget)

    const html = widget.innerHTML
    expect(html).not.toContain('<script>')
    expect(html).toContain('&lt;script&gt;')
    expect(html).not.toContain('<img')
  })

  it('should render edit view with form fields', () => {
    const widget = new ShortcutWidget()
    widget.setAttribute('widget-id', 'test-123')
    widget.setAttribute('url', 'https://example.com')
    widget.setAttribute('title', 'Example')
    widget.setAttribute('icon', '🌟')
    widget.setAttribute('description', 'Test description')
    document.body.appendChild(widget)

    // Trigger edit mode
    widget['setState']('edit')

    const form = widget.querySelector('.widget-edit-form')
    expect(form).toBeTruthy()

    const urlInput = widget.querySelector('#shortcut-url') as HTMLInputElement
    expect(urlInput?.value).toContain('example.com')

    const titleInput = widget.querySelector('#shortcut-title') as HTMLInputElement
    expect(titleInput?.value).toBe('Example')

    const iconInput = widget.querySelector('#shortcut-icon') as HTMLInputElement
    expect(iconInput?.value).toBe('🌟')

    const descriptionInput = widget.querySelector('#shortcut-description') as HTMLTextAreaElement
    expect(descriptionInput?.value).toBe('Test description')
  })

  it('should extract properties from edit form', () => {
    const widget = new ShortcutWidget()
    widget.setAttribute('widget-id', 'test-123')
    document.body.appendChild(widget)

    widget['setState']('edit')

    // Fill in the form
    const urlInput = widget.querySelector('#shortcut-url') as HTMLInputElement
    const titleInput = widget.querySelector('#shortcut-title') as HTMLInputElement
    const iconInput = widget.querySelector('#shortcut-icon') as HTMLInputElement
    const descriptionInput = widget.querySelector('#shortcut-description') as HTMLTextAreaElement

    urlInput.value = 'https://newsite.com'
    titleInput.value = 'New Site'
    iconInput.value = '⭐'
    descriptionInput.value = 'Updated description'

    const properties = widget['extractPropertiesFromForm']()

    expect(properties.url).toBe('https://newsite.com')
    expect(properties.title).toBe('New Site')
    expect(properties.icon).toBe('⭐')
    expect(properties.description).toBe('Updated description')
  })

  it('should handle empty description in form', () => {
    const widget = new ShortcutWidget()
    widget.setAttribute('widget-id', 'test-123')
    document.body.appendChild(widget)

    widget['setState']('edit')

    const urlInput = widget.querySelector('#shortcut-url') as HTMLInputElement
    const titleInput = widget.querySelector('#shortcut-title') as HTMLInputElement
    const descriptionInput = widget.querySelector('#shortcut-description') as HTMLTextAreaElement

    urlInput.value = 'https://example.com'
    titleInput.value = 'Example'
    descriptionInput.value = ''

    const properties = widget['extractPropertiesFromForm']()

    expect(properties.description).toBeNull()
  })

  it('should have save and cancel buttons in edit mode', () => {
    const widget = new ShortcutWidget()
    widget.setAttribute('widget-id', 'test-123')
    document.body.appendChild(widget)

    widget['setState']('edit')

    const saveButton = widget.querySelector('.widget-save-btn')
    const cancelButton = widget.querySelector('.widget-cancel-btn')

    expect(saveButton).toBeTruthy()
    expect(cancelButton).toBeTruthy()
  })

  it('should return to normal view on cancel', () => {
    const widget = new ShortcutWidget()
    widget.setAttribute('widget-id', 'test-123')
    widget.setAttribute('url', 'https://example.com')
    widget.setAttribute('title', 'Example')
    document.body.appendChild(widget)

    // Go to edit mode
    widget['setState']('edit')
    expect(widget.querySelector('.widget-edit-form')).toBeTruthy()

    // Click cancel
    const cancelButton = widget.querySelector('.widget-cancel-btn') as HTMLButtonElement
    cancelButton?.click()

    // Should be back to normal view
    expect(widget.querySelector('.shortcut-link')).toBeTruthy()
    expect(widget.querySelector('.widget-edit-form')).toBeFalsy()
  })
})
