// 실제 Lambda Function URL
const DATA_API_URL = 'https://o5ixcuo7hqxql5desqx4nh7kxe0vruvv.lambda-url.us-east-1.on.aws/'
const WEATHER_API_URL = 'https://62x6xj4s4esb6b4tuioijrgenm0qidmk.lambda-url.us-east-1.on.aws/'

export const api = {
  getBriefing: async (district: string) => {
    const response = await fetch(DATA_API_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ type: 'briefing', district })
    })
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    return response.json()
  },
  
  getDistricts: async () => {
    // 서울시 25개 구 목록
    return { 
      success: true, 
      districts: [
        '강남구', '강동구', '강북구', '강서구', '관악구', '광진구', '구로구', '금천구',
        '노원구', '도봉구', '동대문구', '동작구', '마포구', '서대문구', '서초구', '성동구',
        '성북구', '송파구', '양천구', '영등포구', '용산구', '은평구', '종로구', '중구', '중랑구'
      ] 
    }
  },
  
  getSentimentSummary: async (district: string, days: number = 7) => {
    const response = await fetch(DATA_API_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ type: 'sentiment', district, days })
    })
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    return response.json()
  },
  
  getWeather: async (district: string) => {
    const response = await fetch(WEATHER_API_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ gu_name: district })
    })
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    return response.json()
  },
  
  getRestaurants: async (district: string) => {
    const response = await fetch(DATA_API_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ type: 'restaurants', district })
    })
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    return response.json()
  }
}