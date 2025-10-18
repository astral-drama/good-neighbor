import './style.css'
import { WidgetGrid } from './components/widget-grid'
import { AddWidgetDialog } from './components/add-widget-dialog'

const app = document.querySelector<HTMLDivElement>('#app')!

// Clear default content
app.innerHTML = ''

// Create and mount widget grid
const widgetGrid = new WidgetGrid()
app.appendChild(widgetGrid)

// Create and mount add widget dialog
const addWidgetDialog = new AddWidgetDialog()
app.appendChild(addWidgetDialog)

// Handle add widget requests from the grid
app.addEventListener('add-widget-requested', () => {
  addWidgetDialog.open()
})

// Handle widget creation events from the dialog
app.addEventListener('widget-created', () => {
  void widgetGrid.refresh()
})
