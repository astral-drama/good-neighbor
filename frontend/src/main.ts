import './style.css'
import { WidgetGrid } from './components/widget-grid'
import { AddWidgetDialog } from './components/add-widget-dialog'
import { HomepageSelector } from './components/homepage-selector'

const app = document.querySelector<HTMLDivElement>('#app')!

// Clear default content
app.innerHTML = ''

// Create header with homepage selector
const header = document.createElement('header')
header.className = 'app-header'

const homepageSelector = new HomepageSelector()
header.appendChild(homepageSelector)
app.appendChild(header)

// Create and mount widget grid
const widgetGrid = new WidgetGrid()
app.appendChild(widgetGrid)

// Create and mount add widget dialog
const addWidgetDialog = new AddWidgetDialog()
app.appendChild(addWidgetDialog)

// Handle homepage changes
app.addEventListener('homepage-changed', ((event: CustomEvent<{ homepage: { homepage_id: string; name: string } }>) => {
  console.log('Homepage changed to:', event.detail.homepage)
  // In the future, we'll filter widgets by homepage
  void widgetGrid.refresh()
}) as EventListener)

// Handle add widget requests from the grid
app.addEventListener('add-widget-requested', () => {
  addWidgetDialog.open()
})

// Handle widget creation events from the dialog
app.addEventListener('widget-created', () => {
  void widgetGrid.refresh()
})
