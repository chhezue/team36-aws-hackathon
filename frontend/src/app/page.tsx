'use client'

import { useState } from 'react'
import { FaMapMarkerAlt, FaTh, FaCheck } from 'react-icons/fa'
import { motion } from 'framer-motion'
import Button from '@/components/ui/Button'
import StepIndicator from '@/components/onboarding/StepIndicator'
import LocationSelector from '@/components/onboarding/LocationSelector'
import CategorySelector from '@/components/onboarding/CategorySelector'

export default function OnboardingPage() {
  const [currentStep, setCurrentStep] = useState(1)
  const [selectedGu, setSelectedGu] = useState('')
  const [selectedCategories, setSelectedCategories] = useState<string[]>([])

  const categories = [
    { id: 'weather', name: '날씨 정보' },
    { id: 'community', name: '동네 이슈' },
    { id: 'new_restaurants', name: '신규 개업 음식점' },
    { id: 'hot_restaurants', name: '핫플 음식점' }
  ]

  const nextStep = () => {
    if (currentStep === 1 && !selectedGu) return
    setCurrentStep(prev => prev + 1)
  }

  const toggleCategory = (categoryId: string) => {
    setSelectedCategories(prev => 
      prev.includes(categoryId) 
        ? prev.filter(id => id !== categoryId)
        : [...prev, categoryId]
    )
  }

  const selectAll = () => {
    setSelectedCategories(categories.map(cat => cat.id))
  }

  return (
    <div className="min-h-screen py-8 px-4">
      {/* Step 1: Location */}
      {currentStep === 1 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-8"
        >
          <div className="text-center space-y-6">
            <div className="w-20 h-20 mx-auto glass rounded-2xl flex items-center justify-center animate-glass-appear">
              <FaMapMarkerAlt size={32} className="text-primary-500" />
            </div>
            <div>
              <h1 className="text-h1 text-white mb-3 drop-shadow-lg">VibeThermo</h1>
              <p className="text-body text-white/80 drop-shadow">
                우리 동네 감성 온도를 매일 아침 체크하세요
              </p>
            </div>
          </div>

          <div className="card animate-glass-appear">
            <h2 className="text-h3 text-gray-900 mb-4">거주지 설정</h2>
            <p className="text-small text-gray-600 mb-6">
              정확한 위치 설정으로 맞춤 소식을 받아보세요
            </p>
            <LocationSelector 
              selectedGu={selectedGu}
              onSelect={setSelectedGu}
            />
          </div>

          <button
            onClick={nextStep}
            disabled={!selectedGu}
            className={`w-full py-4 px-6 font-bold text-lg rounded-2xl shadow-xl transition-all duration-300 ${
              !selectedGu 
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed' 
                : 'bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 text-white hover:shadow-2xl hover:scale-105 active:scale-95'
            }`}
          >
            <span className="flex items-center justify-center gap-2">
              다음 단계로
              <span className="text-xl">→</span>
            </span>
          </button>
        </motion.div>
      )}

      {/* Step 2: Categories */}
      {currentStep === 2 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-8"
        >
          <StepIndicator currentStep={currentStep} totalSteps={3} />
          
          <div className="text-center space-y-6">
            <div className="w-20 h-20 mx-auto glass rounded-2xl flex items-center justify-center animate-glass-appear">
              <FaTh size={32} className="text-primary-500" />
            </div>
            <div>
              <h2 className="text-h2 text-white mb-3 drop-shadow-lg">관심 분야 선택</h2>
              <p className="text-body text-white/80 drop-shadow">
                원하는 정보만 골라보세요
              </p>
            </div>
          </div>

          <CategorySelector 
            categories={categories}
            selectedCategories={selectedCategories}
            onToggle={toggleCategory}
            onSelectAll={selectAll}
          />

          <button
            onClick={nextStep}
            className="w-full py-4 px-6 bg-gradient-to-r from-emerald-500 via-teal-500 to-cyan-500 text-white font-bold text-lg rounded-2xl shadow-xl hover:shadow-2xl hover:scale-105 active:scale-95 transition-all duration-300"
          >
            <span className="flex items-center justify-center gap-2">
              설정 완료
              <span className="text-xl">✨</span>
            </span>
          </button>
        </motion.div>
      )}

      {/* Step 3: Complete */}
      {currentStep === 3 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center space-y-8"
        >
          <div className="space-y-6">
            <div className="w-24 h-24 mx-auto glass rounded-2xl flex items-center justify-center animate-glass-appear">
              <FaCheck size={32} className="text-green-500" />
            </div>
            <div>
              <h2 className="text-h1 text-white mb-3 drop-shadow-lg">설정 완료!</h2>
              <p className="text-body text-white/80 drop-shadow">
                매일 아침 7시에 맞춤 브리핑을 받아보세요
              </p>
            </div>
          </div>

          <div className="space-y-4">
            <button
              onClick={() => {
                localStorage.setItem('selectedDistrict', selectedGu)
                localStorage.setItem('selectedCategories', JSON.stringify(selectedCategories))
                window.location.href = '/briefing'
              }}
              className="w-full py-5 px-6 bg-gradient-to-r from-violet-600 via-purple-600 to-indigo-600 text-white font-black text-xl rounded-2xl shadow-2xl hover:shadow-3xl hover:scale-105 active:scale-95 transition-all duration-300 border-0"
            >
              <span className="flex items-center justify-center gap-3">
                <span className="text-2xl">🚀</span>
                브리핑 보러가기
                <span className="text-2xl">🚀</span>
              </span>
            </button>
          </div>
        </motion.div>
      )}
    </div>
  )
}