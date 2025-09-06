// 백엔드 기반 Lambda Function URL
const API_BASE_URL = 'https://giamfpvxd3iohvg22bvpsqifwy0aodcs.lambda-url.us-east-1.on.aws'

export const api = {
  getBriefing: async (district: string) => {
    const response = await fetch(`${API_BASE_URL}?type=briefing&district=${encodeURIComponent(district)}`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' }
    })
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    return response.json()
  },
  
  getDistricts: async () => {
    const response = await fetch(`${API_BASE_URL}?type=districts`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' }
    })
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    return response.json()
  },
  
  getSentimentSummary: async (district: string, days: number = 7) => {
    const response = await fetch(`${API_BASE_URL}?type=sentiment&district=${encodeURIComponent(district)}&days=${days}`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' }
    })
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    return response.json()
  },
  
  getWeather: async (district: string) => {
    const response = await fetch(`${API_BASE_URL}?type=weather&district=${encodeURIComponent(district)}`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' }
    })
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    return response.json()
  },
  
  getRestaurants: async (district: string) => {
    const response = await fetch(`${API_BASE_URL}?type=restaurants&district=${encodeURIComponent(district)}`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' }
    })
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    return response.json()
  }
}