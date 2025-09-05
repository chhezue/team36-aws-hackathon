'use client'

import { useState, useEffect } from 'react'
import { HiLocationMarker, HiViewGrid, HiBell, HiSun, HiChat, HiSparkles } from 'react-icons/hi'
import { motion } from 'framer-motion'
import Header from '@/components/layout/Header'
import Card from '@/components/ui/Card'
import Toggle from '@/components/ui/Toggle'
import Button from '@/components/ui/Button'
import Modal from '@/components/ui/Modal'
import Skeleton from '@/components/ui/Skeleton'
import { api } from '@/lib/api'

export default function SettingsPage() {
  const [categories, setCategories] = useState({
    weather: true,
    community: true,
    restaurants: true,
    newRestaurants: true
  })
  const [notificationTime, setNotificationTime] = useState('07:00')
  const [weekendNotifications, setWeekendNotifications] = useState(true)
  const [showLocationModal, setShowLocationModal] = useState(false)
  const [selectedDistrict, setSelectedDistrict] = useState('강남구')
  const [districts, setDistricts] = useState<string[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchDistricts = async () => {
      try {
        setLoading(true)
        const data = await api.getDistricts()
        setDistricts(data.districts || [])
      } catch (error) {
        console.error('구 데이터 로드 실패:', error)
      } finally {
        setLoading(false)
      }
    }
    fetchDistricts()
    
    // 저장된 설정 로드
    const savedSettings = localStorage.getItem('briefingSettings')
    if (savedSettings) {
      const settings = JSON.parse(savedSettings)
      setCategories(settings.categories || categories)
      setNotificationTime(settings.notificationTime || '07:00')
      setWeekendNotifications(settings.weekendNotifications ?? true)
      setSelectedDistrict(settings.district || '강남구')
    }
  }, [])

  const toggleCategory = (category: keyof typeof categories) => {
    setCategories(prev => ({
      ...prev,
      [category]: !prev[category]
    }))
  }

  const saveSettings = async () => {
    try {
      // 로컬 스토리지에 설정 저장
      const settings = {
        categories,
        notificationTime,
        weekendNotifications,
        district: selectedDistrict
      }
      localStorage.setItem('briefingSettings', JSON.stringify(settings))
      alert('설정이 저장되었습니다.')
    } catch (error) {
      console.error('설정 저장 실패:', error)
    }
  }

  return (
    <div className="min-h-screen py-6 space-y-6">
      <Header 
        title="설정"
        subtitle="내 브리핑을 맞춤 설정하세요"
        showBack
        onBack={() => window.location.href = '/briefing'}
      />



      {/* Location Card */}
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="card"
      >
        <div className="flex items-center gap-4 mb-4">
          <div className="w-10 h-10 bg-primary-50 rounded-lg flex items-center justify-center">
            <HiLocationMarker size={20} className="text-primary-500" />
          </div>
          <div>
            <h3 className="text-h3 text-gray-900">거주지 설정</h3>
            <p className="text-small text-gray-600">정확한 위치로 맞춤 소식을 받아보세요</p>
          </div>
        </div>
        <div className="flex justify-between items-center p-4 bg-gray-50 rounded-xl">
          <div className="flex items-center gap-2">
            <span>🏠</span>
            <span className="font-medium text-gray-900">{selectedDistrict}</span>
          </div>
          <button 
            onClick={() => setShowLocationModal(true)}
            className="btn btn-primary"
          >
            변경
          </button>
        </div>
      </motion.div>

      {/* Categories Card */}
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="card"
      >
        <div className="flex items-center gap-4 mb-4">
          <div className="w-10 h-10 bg-primary-50 rounded-lg flex items-center justify-center">
            <HiViewGrid size={20} className="text-primary-500" />
          </div>
          <div>
            <h3 className="text-h3 text-gray-900">브리핑 카테고리</h3>
            <p className="text-small text-gray-600">받고 싶은 정보를 선택하세요</p>
          </div>
        </div>
        <div className="space-y-4">
          {[
            { key: 'weather', name: '날씨 정보', IconComponent: HiSun },
            { key: 'community', name: '동네 이슈', IconComponent: HiChat },
            { key: 'restaurants', name: '맛집 정보', IconComponent: HiLocationMarker },
            { key: 'newRestaurants', name: '신규 개업', IconComponent: HiSparkles }
          ].map(category => (
            <div key={category.key} className="flex justify-between items-center p-4 bg-gray-50 rounded-xl">
              <div className="flex items-center gap-3">
                <category.IconComponent className="text-xl text-primary-500" />
                <span className="text-body font-medium text-gray-900">{category.name}</span>
              </div>
              <button
                onClick={() => toggleCategory(category.key as keyof typeof categories)}
                className={`w-12 h-6 rounded-full transition-colors ${
                  categories[category.key as keyof typeof categories] 
                    ? 'bg-primary-500' 
                    : 'bg-gray-300'
                }`}
              >
                <div className={`w-5 h-5 bg-white rounded-full transition-transform ${
                  categories[category.key as keyof typeof categories] 
                    ? 'translate-x-6' 
                    : 'translate-x-0.5'
                }`} />
              </button>
            </div>
          ))}
        </div>
      </motion.div>

      {/* Notifications Card */}
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="card"
      >
        <div className="flex items-center gap-4 mb-4">
          <div className="w-10 h-10 bg-primary-50 rounded-lg flex items-center justify-center">
            <HiBell size={20} className="text-primary-500" />
          </div>
          <div>
            <h3 className="text-h3 text-gray-900">알림 설정</h3>
            <p className="text-small text-gray-600">브리핑 알림을 관리하세요</p>
          </div>
        </div>
        <div className="space-y-4">
          <div className="flex justify-between items-center p-4 bg-gray-50 rounded-xl">
            <div className="flex items-center gap-2">
              <span>🕐</span>
              <span className="text-body text-gray-900">브리핑 시간</span>
            </div>
            <select 
              value={notificationTime}
              onChange={(e) => setNotificationTime(e.target.value)}
              className="px-3 py-2 bg-white border border-gray-200 rounded-lg text-small"
            >
              <option value="06:00">오전 6:00</option>
              <option value="07:00">오전 7:00</option>
              <option value="08:00">오전 8:00</option>
              <option value="09:00">오전 9:00</option>
              <option value="10:00">오전 10:00</option>
            </select>
          </div>
          <div className="flex justify-between items-center p-4 bg-gray-50 rounded-xl">
            <div className="flex items-center gap-2">
              <span>📅</span>
              <span className="text-body text-gray-900">주말 알림</span>
            </div>
            <button
              onClick={() => setWeekendNotifications(!weekendNotifications)}
              className={`w-12 h-6 rounded-full transition-colors ${
                weekendNotifications ? 'bg-primary-500' : 'bg-gray-300'
              }`}
            >
              <div className={`w-5 h-5 bg-white rounded-full transition-transform ${
                weekendNotifications ? 'translate-x-6' : 'translate-x-0.5'
              }`} />
            </button>
          </div>
        </div>
      </motion.div>

      <Button onClick={saveSettings}>
        설정 저장
      </Button>

      {/* Location Modal */}
      {showLocationModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <motion.div 
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-white rounded-2xl p-6 w-full max-w-sm"
          >
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold">거주지 변경</h3>
              <button 
                onClick={() => setShowLocationModal(false)}
                className="p-1"
              >
                ✕
              </button>
            </div>
            <div className="space-y-4">
              {loading ? (
                <Skeleton className="w-full h-12 rounded-lg" />
              ) : (
                <select 
                  value={selectedDistrict}
                  onChange={(e) => setSelectedDistrict(e.target.value)}
                  className="w-full p-3 border border-gray-200 rounded-lg"
                >
                  {districts.map(district => (
                    <option key={district} value={district}>{district}</option>
                  ))}
                </select>
              )}
              <div className="flex gap-3">
                <button 
                  onClick={() => setShowLocationModal(false)}
                  className="flex-1 btn-secondary"
                >
                  취소
                </button>
                <button 
                  onClick={() => setShowLocationModal(false)}
                  className="flex-1 btn-primary"
                >
                  저장
                </button>
              </div>
            </div>
          </motion.div>
        </div>
      )}
    </div>
  )
}