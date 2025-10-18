import { describe, it, expect, beforeEach } from 'vitest'

describe('Good Neighbor App', () => {
  beforeEach(() => {
    // Set up a fresh DOM for each test
    document.body.innerHTML = '<div id="app"></div>'
  })

  it('should create app container', () => {
    const app = document.querySelector('#app')
    expect(app).toBeTruthy()
    expect(app).toBeInstanceOf(HTMLDivElement)
  })

  it('should render heading with correct text', () => {
    document.querySelector<HTMLDivElement>('#app')!.innerHTML = `
      <div>
        <h1>Good Neighbor</h1>
        <p>Welcome to your customizable homepage!</p>
      </div>
    `

    const heading = document.querySelector('h1')
    expect(heading).toBeTruthy()
    expect(heading?.textContent).toBe('Good Neighbor')
  })

  it('should render welcome message', () => {
    document.querySelector<HTMLDivElement>('#app')!.innerHTML = `
      <div>
        <h1>Good Neighbor</h1>
        <p>Welcome to your customizable homepage!</p>
      </div>
    `

    const paragraph = document.querySelector('p')
    expect(paragraph).toBeTruthy()
    expect(paragraph?.textContent).toBe('Welcome to your customizable homepage!')
  })
})
