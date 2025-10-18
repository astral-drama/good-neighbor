import './style.css'

const app = document.querySelector<HTMLDivElement>('#app')!

app.innerHTML = `
  <div>
    <h1>Good Neighbor</h1>
    <p>Welcome to your customizable homepage Seth!</p>
    <div id="api-status">
      <p>Checking API connection...</p>
    </div>
  </div>
`

// Test API connection
async function checkAPI() {
  const statusDiv = document.querySelector('#api-status')!
  try {
    const response = await fetch('/api/health')
    const data: unknown = await response.json()
    statusDiv.innerHTML = `<p style="color: green;">✓ API Connected: ${JSON.stringify(data)}</p>`
  } catch {
    statusDiv.innerHTML = `<p style="color: orange;">⚠ API not available (this is normal in dev mode before backend starts)</p>`
  }
}

void checkAPI()
