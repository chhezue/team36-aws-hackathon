'use client'

import { useState, useEffect } from 'react'
import { HiSun, HiChat, HiLocationMarker, HiSparkles } from 'react-icons/hi'
import Header from '@/components/layout/Header'
import WeatherCard from '@/components/briefing/WeatherCard'
import NewsCard from '@/components/briefing/NewsCard'
import SentimentModal from '@/components/briefing/SentimentModal'
import Button from '@/components/ui/Button'
import { WeatherSkeleton, NewsSkeleton } from '@/components/ui/Skeleton'
import { api } from '@/lib/api'

interface BriefingData {
  weather: {
    condition: string
    temperature: number
    dust: string
    emoji: string
  }
  community: Array<{
    title: string
    source: string
  }>
  restaurants: Array<{
    title: string
    type: string
  }>
  newRestaurants: Array<{
    title: string
    location: string
  }>
}

export default function BriefingPage() {
  const [briefingData, setBriefingData] = useState<BriefingData | null>(null)
  const [selectedDate, setSelectedDate] = useState(new Date())
  const [showSentimentModal, setShowSentimentModal] = useState(false)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchBriefingData()
  }, [selectedDate])

  const fetchBriefingData = async () => {
    try {
      setLoading(true)
      const data = await api.getBriefing('강남구')
      setBriefingData(data)
    } catch (error) {
      console.error('브리핑 데이터 로드 실패:', error)
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
        subtitle={`📍 강남구\n${formatDate(selectedDate)}`}
        showSentiment
        showSettings
        onSentiment={() => setShowSentimentModal(true)}
        onSettings={() => window.location.href = '/settings'}
      />

      {loading ? (
        <WeatherSkeleton />
      ) : (
        <WeatherCard 
          condition="맑음"
          temperature={18}
          dust="보통"
          description={briefingData?.sentiment?.description || "오늘의 동네 분위기를 확인해보세요"}
        />
      )}

      {loading ? (
        <NewsSkeleton />
      ) : (
        <NewsCard 
          title="동네 분위기"
          IconComponent={HiChat}
          items={briefingData?.issues?.map(issue => ({
            title: issue.title,
            source: issue.source,
            sentiment: issue.sentiment_impact > 0 ? 'sunny' : issue.sentiment_impact < 0 ? 'stormy' : 'cloudy'
          })) || []}
          delay={0.1}
        />
      )}

      {loading ? (
        <NewsSkeleton />
      ) : (
        <NewsCard 
          title="맛집 온도"
          IconComponent={HiLocationMarker}
          items={briefingData?.issues?.filter(issue => issue.source.includes('맛집')).map(issue => ({
            title: issue.title,
            source: issue.source,
            sentiment: 'warm'
          })) || [
            { title: "맛집 정보를 수집 중입니다", source: "시스템", sentiment: "warm" }
          ]}
          delay={0.2}
        />
      )}

      {loading ? (
        <NewsSkeleton />
      ) : (
        <NewsCard 
          title="신선한 맛집"
          IconComponent={HiSparkles}
          items={briefingData?.issues?.filter(issue => issue.source.includes('신규')).map(issue => ({
            title: issue.title,
            source: issue.source,
            sentiment: 'cool'
          })) || [
            { title: "신규 맛집 정보를 수집 중입니다", source: "시스템", sentiment: "cool" }
          ]}
          delay={0.3}
        />
      )}

      <SentimentModal 
        isOpen={showSentimentModal}
        onClose={() => setShowSentimentModal(false)}
        sentiment={{
          positiveRatio: briefingData?.sentiment?.temperature || 50,
          negativeRatio: 100 - (briefingData?.sentiment?.temperature || 50),
          moodEmoji: briefingData?.sentiment?.mood_emoji || "☀️"
        }}
      />
    </div>
  )
}