const API_BASE_URL = 'http://localhost:8000'

export const api = {
  getBriefing: async (district: string) => {
    const response = await fetch(`${API_BASE_URL}/api/briefing/?district=${district}`)
    return response.json()
  },
  
  getDistricts: async () => {
    const response = await fetch(`${API_BASE_URL}/api/location/districts/`)
    return response.json()
  },
  
  getSentimentSummary: async (district: string, days: number = 7) => {
    const response = await fetch(`${API_BASE_URL}/api/sentiment/summary/?district=${district}&days=${days}`)
    return response.json()
  },
  
  getWeather: async (district: string) => {
    const response = await fetch(`${API_BASE_URL}/api/weather/?district=${district}`)
    return response.json()
  }
}