export interface WeatherInfo {
  condition: string
  temperature: number
  dust: string
  emoji: string
  description: string
}

export interface CommunityIssue {
  id: number
  title: string
  source: 'youtube' | 'naver_search' | 'naver_news'
  url: string
  viewCount: number
  publishedAt: string
}

export interface RestaurantInfo {
  id: number
  businessName: string
  businessType: string
  address: string
  licenseDate: string
}

export interface SentimentData {
  sentiment: 'positive' | 'negative' | 'neutral'
  confidence: number
  keywords: string[]
  positiveRatio: number
  negativeRatio: number
  moodEmoji: string
}

export interface BriefingData {
  date: string
  location: string
  weather: WeatherInfo
  community: CommunityIssue[]
  restaurants: RestaurantInfo[]
  newRestaurants: RestaurantInfo[]
  sentiment: SentimentData
}

export interface UserSettings {
  district: string
  categories: {
    weather: boolean
    community: boolean
    restaurants: boolean
    newRestaurants: boolean
  }
  notificationTime: string
  weekendNotifications: boolean
}