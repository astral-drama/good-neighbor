/**
 * Homepage API client for interacting with the backend
 */

import type { Homepage, CreateHomepageRequest, UpdateHomepageRequest } from '../types/homepage'

// Use relative path to work with base path configuration
const API_BASE_URL = ''

/**
 * Fetch all homepages for the current user
 */
export async function listHomepages(): Promise<Homepage[]> {
  const response = await fetch(`${API_BASE_URL}/api/homepages/`)
  if (!response.ok) {
    throw new Error(`Failed to list homepages: ${response.statusText}`)
  }
  return response.json() as Promise<Homepage[]>
}

/**
 * Get a specific homepage by ID
 */
export async function getHomepage(homepageId: string): Promise<Homepage> {
  const response = await fetch(`${API_BASE_URL}/api/homepages/${homepageId}`)
  if (!response.ok) {
    throw new Error(`Failed to get homepage: ${response.statusText}`)
  }
  return response.json() as Promise<Homepage>
}

/**
 * Create a new homepage
 */
export async function createHomepage(request: CreateHomepageRequest): Promise<Homepage> {
  const response = await fetch(`${API_BASE_URL}/api/homepages/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  })
  if (!response.ok) {
    throw new Error(`Failed to create homepage: ${response.statusText}`)
  }
  return response.json() as Promise<Homepage>
}

/**
 * Update a homepage's name
 */
export async function updateHomepage(
  homepageId: string,
  request: UpdateHomepageRequest
): Promise<Homepage> {
  const response = await fetch(`${API_BASE_URL}/api/homepages/${homepageId}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  })
  if (!response.ok) {
    throw new Error(`Failed to update homepage: ${response.statusText}`)
  }
  return response.json() as Promise<Homepage>
}

/**
 * Set a homepage as the default
 */
export async function setDefaultHomepage(homepageId: string): Promise<Homepage> {
  const response = await fetch(`${API_BASE_URL}/api/homepages/${homepageId}/default`, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ is_default: true }),
  })
  if (!response.ok) {
    throw new Error(`Failed to set default homepage: ${response.statusText}`)
  }
  return response.json() as Promise<Homepage>
}

/**
 * Delete a homepage
 */
export async function deleteHomepage(homepageId: string): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/api/homepages/${homepageId}`, {
    method: 'DELETE',
  })
  if (!response.ok) {
    const errorData = (await response.json().catch(() => ({ detail: response.statusText }))) as { detail?: string }
    throw new Error(`Failed to delete homepage: ${errorData.detail ?? response.statusText}`)
  }
}

/**
 * Get or create the default homepage
 * Returns the first homepage if available, or creates a new one
 */
export async function getOrCreateDefaultHomepage(): Promise<Homepage> {
  const homepages = await listHomepages()

  if (homepages.length === 0) {
    // Create a default homepage
    return createHomepage({ name: 'Home', is_default: true })
  }

  // Return the default homepage, or the first one if no default is set
  return homepages.find(hp => hp.is_default) || homepages[0]
}
