'use client'

import { useState, useEffect } from 'react'
import { HiSun, HiChat, HiLocationMarker, HiSparkles } from 'react-icons/hi'
import Header from '@/components/layout/Header'
import RealWeatherCard from '@/components/briefing/RealWeatherCard'
import SentimentCard from '@/components/briefing/SentimentCard'
import NewsCard from '@/components/briefing/NewsCard'
import SentimentModal from '@/components/briefing/SentimentModal'
import Button from '@/components/ui/Button'
import { WeatherSkeleton, NewsSkeleton } from '@/components/ui/Skeleton'
import { api } from '@/lib/api'

interface BriefingData {
  success: boolean
  district: string
  date: string
  sentiment: {
    temperature: number
    mood_emoji: string
    description: string
    positive_ratio: number
    negative_ratio: number
  }
  categories: {
    local_issues: {
      title: string
      emoji: string
      items: Array<{
        title: string
        source: string
        url: string
        view_count: number
        collected_at: string
      }>
    }
    announcements: {
      title: string
      emoji: string
      items: Array<{
        title: string
        department: string
        view_count: number
        created_at: string
      }>
    }
    new_restaurants: {
      title: string
      emoji: string
      items: Array<{
        name: string
        type: string
        address: string
        license_date: string
      }>
    }
  }
}

interface WeatherData {
  success: boolean
  district: string
  weather: {
    temp: string
    condition: string
    dust: string
    description: string
    hourly_forecast: Array<{
      time: string
      temp: string
      condition: string
    }>
  }
}

export default function BriefingPage() {
  const [briefingData, setBriefingData] = useState<BriefingData | null>(null)
  const [weatherData, setWeatherData] = useState<WeatherData | null>(null)
  const [selectedDate, setSelectedDate] = useState(new Date())
  const [showSentimentModal, setShowSentimentModal] = useState(false)
  const [loading, setLoading] = useState(true)
  const [selectedDistrict, setSelectedDistrict] = useState('강남구')

  useEffect(() => {
    // localStorage에서 선택한 구 가져오기
    const savedDistrict = localStorage.getItem('selectedDistrict')
    if (savedDistrict) {
      setSelectedDistrict(savedDistrict)
    }
  }, [])
  
  useEffect(() => {
    fetchBriefingData()
  }, [selectedDate, selectedDistrict])

  const fetchBriefingData = async () => {
    try {
      setLoading(true)
      const [briefingResponse, weatherResponse] = await Promise.all([
        api.getBriefing(selectedDistrict),
        api.getWeather(selectedDistrict)
      ])
      
      console.log('=== API 응답 디버깅 ===');
      console.log('브리핑 데이터:', briefingResponse)
      console.log('브리핑 성공:', briefingResponse.success)
      console.log('동네 이슈 개수:', briefingResponse?.categories?.local_issues?.items?.length || 0)
      console.log('날씨 데이터:', weatherResponse)
      console.log('========================')
      
      if (briefingResponse.success) {
        setBriefingData(briefingResponse)
      } else {
        console.error('브리핑 데이터 오류:', briefingResponse.error)
      }
      
      if (weatherResponse.success) {
        setWeatherData(weatherResponse)
      } else {
        console.error('날씨 데이터 오류:', weatherResponse.error)
      }
    } catch (error) {
      console.error('데이터 로드 실패:', error)
    } finally {
      setLoading(false)
    }
  }

  const formatDate = (date: Date) => {
    const days = ['일', '월', '화', '수', '목', '금', '토']
    const year = date.getFullYear()
    const month = date.getMonth() + 1
    const day = date.getDate()
    const dayName = days[date.getDay()]
    
    return `${year}년 ${month}월 ${day}일 ${dayName}요일`
  }

  return (
    <div className="min-h-screen py-6 space-y-6">
      <Header 
        title="LocalBriefing"
        subtitle={`📍 ${selectedDistrict}\n${formatDate(selectedDate)}`}
        showSentiment
        showSettings
        onSentiment={() => setShowSentimentModal(true)}
        onSettings={() => window.location.href = '/settings'}
      />

      {loading ? (
        <WeatherSkeleton />
      ) : briefingData?.sentiment ? (
        <SentimentCard 
          temperature={briefingData.sentiment.temperature}
          moodEmoji={briefingData.sentiment.mood_emoji}
          description={briefingData.sentiment.description}
          onClick={() => setShowSentimentModal(true)}
        />
      ) : (
        <WeatherSkeleton />
      )}

      {loading ? (
        <WeatherSkeleton />
      ) : weatherData?.weather ? (
        <RealWeatherCard 
          condition={weatherData.weather.condition}
          temp={weatherData.weather.temp}
          dust={weatherData.weather.dust}
          description={weatherData.weather.description}
          hourlyForecast={weatherData.weather.hourly_forecast}
        />
      ) : (
        <WeatherSkeleton />
      )}

      {loading ? (
        <NewsSkeleton />
      ) : (
        <NewsCard 
          title={briefingData?.categories?.local_issues?.title || "동네 이슈"}
          IconComponent={HiChat}
          items={briefingData?.categories?.local_issues?.items?.map(issue => ({
            title: issue.title,
            source: issue.source,
            sentiment: 'cloudy',
            url: issue.url,
            viewCount: issue.view_count
          })) || []}
          delay={0.1}
        />
      )}

      {loading ? (
        <NewsSkeleton />
      ) : (
        <NewsCard 
          title={briefingData?.categories?.new_restaurants?.title || "신규 개업 음식점"}
          IconComponent={HiSparkles}
          items={briefingData?.categories?.new_restaurants?.items?.map(restaurant => ({
            title: restaurant.name,
            source: restaurant.type,
            sentiment: 'cool',
            address: restaurant.address
          })) || []}
          delay={0.2}
        />
      )}

      {loading ? (
        <NewsSkeleton />
      ) : (
        <NewsCard 
          title="핫플 음식점"
          IconComponent={HiLocationMarker}
          items={[]}
          delay={0.3}
        />
      )}

      {briefingData?.sentiment && (
        <SentimentModal 
          isOpen={showSentimentModal}
          onClose={() => setShowSentimentModal(false)}
          sentiment={{
            positiveRatio: briefingData.sentiment.positive_ratio,
            negativeRatio: briefingData.sentiment.negative_ratio,
            moodEmoji: briefingData.sentiment.mood_emoji
          }}
        />
      )}
    </div>
  )
}