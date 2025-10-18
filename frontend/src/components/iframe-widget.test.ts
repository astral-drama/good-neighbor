import { describe, it, expect, beforeEach } from 'vitest'
import { IframeWidget } from './iframe-widget'

describe('IframeWidget', () => {
  beforeEach(() => {
    document.body.innerHTML = '<div id="test-container"></div>'
  })

  it('should render normal view with iframe', () => {
    const widget = new IframeWidget()
    widget.setAttribute('widget-id', 'test-123')
    widget.setAttribute('url', 'https://example.com')
    widget.setAttribute('title', 'Test Iframe')
    widget.setAttribute('width', '400')
    widget.setAttribute('height', '300')
    document.body.appendChild(widget)

    const iframe = widget.querySelector('iframe')
    expect(iframe).toBeTruthy()
    expect(iframe?.getAttribute('src')).toContain('example.com')
    expect(iframe?.getAttribute('width')).toBe('400')
    expect(iframe?.getAttribute('height')).toBe('300')
    expect(iframe?.getAttribute('sandbox')).toContain('allow-scripts')
  })

  it('should render title in normal view', () => {
    const widget = new IframeWidget()
    widget.setAttribute('widget-id', 'test-123')
    widget.setAttribute('url', 'https://example.com')
    widget.setAttribute('title', 'My Test Widget')
    document.body.appendChild(widget)

    const title = widget.querySelector('.widget-title')
    expect(title?.textContent).toBe('My Test Widget')
  })

  it('should use default values when attributes are missing', () => {
    const widget = new IframeWidget()
    widget.setAttribute('widget-id', 'test-123')
    document.body.appendChild(widget)

    const title = widget.querySelector('.widget-title')
    expect(title?.textContent).toBe('Iframe Widget')

    const iframe = widget.querySelector('iframe')
    expect(iframe?.getAttribute('width')).toBe('400')
    expect(iframe?.getAttribute('height')).toBe('300')
  })

  it('should escape HTML in title attribute', () => {
    const widget = new IframeWidget()
    widget.setAttribute('widget-id', 'test-123')
    widget.setAttribute('title', '<script>alert("xss")</script>')
    widget.setAttribute('url', 'https://example.com')
    document.body.appendChild(widget)

    const title = widget.querySelector('.widget-title')
    // Should escape the script tags
    expect(title?.innerHTML).toContain('&lt;script&gt;')
    expect(title?.innerHTML).toContain('&lt;/script&gt;')
    // Should not contain actual script tags
    expect(title?.innerHTML).not.toMatch(/<script/i)
  })

  it('should render edit view with form fields', () => {
    const widget = new IframeWidget()
    widget.setAttribute('widget-id', 'test-123')
    widget.setAttribute('url', 'https://example.com')
    widget.setAttribute('title', 'Test Widget')
    widget.setAttribute('width', '500')
    widget.setAttribute('height', '400')
    document.body.appendChild(widget)

    // Trigger edit mode directly
    widget['setState']('edit')

    const form = widget.querySelector('.widget-edit-form')
    expect(form).toBeTruthy()

    const urlInput = widget.querySelector('#iframe-url') as HTMLInputElement
    expect(urlInput?.value).toContain('example.com')

    const titleInput = widget.querySelector('#iframe-title') as HTMLInputElement
    expect(titleInput?.value).toBe('Test Widget')

    const widthInput = widget.querySelector('#iframe-width') as HTMLInputElement
    expect(widthInput?.value).toBe('500')
  })

  it('should have save and cancel buttons in edit mode', () => {
    const widget = new IframeWidget()
    widget.setAttribute('widget-id', 'test-123')
    document.body.appendChild(widget)

    // Trigger edit mode by setting state
    widget['setState']('edit')

    const saveButton = widget.querySelector('.widget-save-btn')
    const cancelButton = widget.querySelector('.widget-cancel-btn')

    expect(saveButton).toBeTruthy()
    expect(cancelButton).toBeTruthy()
  })

  it('should return to normal view on cancel', () => {
    const widget = new IframeWidget()
    widget.setAttribute('widget-id', 'test-123')
    widget.setAttribute('url', 'https://example.com')
    document.body.appendChild(widget)

    // Go to edit mode
    widget['setState']('edit')
    expect(widget.querySelector('.widget-edit-form')).toBeTruthy()

    // Click cancel
    const cancelButton = widget.querySelector('.widget-cancel-btn') as HTMLButtonElement
    cancelButton?.click()

    // Should be back to normal view
    expect(widget.querySelector('iframe')).toBeTruthy()
    expect(widget.querySelector('.widget-edit-form')).toBeFalsy()
  })

  it('should extract properties from edit form', () => {
    const widget = new IframeWidget()
    widget.setAttribute('widget-id', 'test-123')
    document.body.appendChild(widget)

    widget['setState']('edit')

    // Fill in the form
    const urlInput = widget.querySelector('#iframe-url') as HTMLInputElement
    const titleInput = widget.querySelector('#iframe-title') as HTMLInputElement
    const widthInput = widget.querySelector('#iframe-width') as HTMLInputElement
    const heightInput = widget.querySelector('#iframe-height') as HTMLInputElement

    urlInput.value = 'https://test.com'
    titleInput.value = 'New Title'
    widthInput.value = '600'
    heightInput.value = '450'

    const properties = widget['extractPropertiesFromForm']()

    expect(properties.url).toBe('https://test.com')
    expect(properties.title).toBe('New Title')
    expect(properties.width).toBe(600)
    expect(properties.height).toBe(450)
  })

  it('should handle refresh interval attribute', () => {
    const widget = new IframeWidget()
    widget.setAttribute('widget-id', 'test-123')
    widget.setAttribute('url', 'https://example.com')
    widget.setAttribute('refresh-interval', '30')
    document.body.appendChild(widget)

    // Should have the attribute set
    expect(widget.getAttribute('refresh-interval')).toBe('30')
  })
})
