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
            <div className="w-20 h-20 mx-auto bg-primary-50 rounded-2xl flex items-center justify-center">
              <FaMapMarkerAlt size={32} className="text-primary-500" />
            </div>
            <div>
              <h1 className="text-h1 text-gray-900 mb-3">LocalBriefing</h1>
              <p className="text-body text-gray-600">
                우리 동네 소식을 매일 아침 받아보세요
              </p>
            </div>
          </div>

          <div className="card">
            <h2 className="text-h3 text-gray-900 mb-4">거주지 설정</h2>
            <p className="text-small text-gray-600 mb-6">
              정확한 위치 설정으로 맞춤 소식을 받아보세요
            </p>
            <LocationSelector 
              selectedGu={selectedGu}
              onSelect={setSelectedGu}
            />
          </div>

          <Button 
            onClick={nextStep}
            disabled={!selectedGu}
            className="w-full"
          >
            다음
          </Button>
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
            <div className="w-20 h-20 mx-auto bg-primary-50 rounded-2xl flex items-center justify-center">
              <FaTh size={32} className="text-primary-500" />
            </div>
            <div>
              <h2 className="text-h2 text-gray-900 mb-3">관심 분야 선택</h2>
              <p className="text-body text-gray-600">
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

          <Button onClick={nextStep} className="w-full">
            완료
          </Button>
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
            <div className="w-24 h-24 mx-auto bg-success/10 rounded-2xl flex items-center justify-center">
              <FaCheck size={32} className="text-green-500" />
            </div>
            <div>
              <h2 className="text-h1 text-gray-900 mb-3">설정 완료!</h2>
              <p className="text-body text-gray-600">
                매일 아침 7시에 맞춤 브리핑을 받아보세요
              </p>
            </div>
          </div>

          <div className="space-y-4">
            <Button onClick={() => {
              localStorage.setItem('selectedDistrict', selectedGu)
              localStorage.setItem('selectedCategories', JSON.stringify(selectedCategories))
              window.location.href = '/briefing'
            }} className="w-full">
              브리핑 보러가기
            </Button>
          </div>
        </motion.div>
      )}
    </div>
  )
}