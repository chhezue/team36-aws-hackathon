import Modal from '../ui/Modal'
import { FaSun, FaCloudRain, FaThermometerHalf, FaNewspaper } from 'react-icons/fa'
import { motion } from 'framer-motion'

interface NewsItem {
  title: string
  source: string
  url?: string
  view_count?: number
  collected_at?: string
}

interface SentimentModalProps {
  isOpen: boolean
  onClose: () => void
  sentiment: {
    positiveRatio: number
    negativeRatio: number
    moodEmoji: string
  }
  influentialNews?: NewsItem[]
}

const getWeatherDescription = (positiveRatio: number, negativeRatio: number) => {
  if (positiveRatio > 70) return { text: '맑은 날씨', icon: <FaSun className="text-4xl text-white" />, color: 'text-yellow-500', gradient: 'from-yellow-400 to-orange-400' }
  if (positiveRatio > 50) return { text: '따뜻한 날씨', icon: <FaSun className="text-4xl text-white" />, color: 'text-orange-500', gradient: 'from-orange-400 to-red-400' }
  if (negativeRatio > 50) return { text: '흐린 날씨', icon: <FaCloudRain className="text-4xl text-white" />, color: 'text-gray-500', gradient: 'from-gray-400 to-blue-400' }
  if (negativeRatio > 70) return { text: '비오는 날씨', icon: <FaCloudRain className="text-4xl text-white" />, color: 'text-blue-500', gradient: 'from-blue-400 to-indigo-500' }
  return { text: '보통 날씨', icon: <FaCloudRain className="text-4xl text-white" />, color: 'text-gray-500', gradient: 'from-gray-400 to-blue-400' }
}

export default function SentimentModal({ isOpen, onClose, sentiment, influentialNews = [] }: SentimentModalProps) {
  const weather = getWeatherDescription(sentiment.positiveRatio, sentiment.negativeRatio)
  
  return (
    <Modal isOpen={isOpen} onClose={onClose} title="동네 감성 온도">
      <div className="space-y-8">
        {/* 메인 온도 섹션 */}
        <div className="text-center space-y-6">
          <motion.div 
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ duration: 0.5, type: "spring" }}
            className={`inline-flex items-center justify-center w-24 h-24 rounded-full bg-gradient-to-br ${weather.gradient} shadow-2xl`}
          >
            <div className="text-white">{weather.icon}</div>
          </motion.div>
          
          <p className={`text-xl font-bold ${weather.color}`}>
            오늘 동네는 {weather.text}예요
          </p>
        </div>

        {/* 영향을 준 뉴스 섹션 */}
        <div className="border-t border-gray-200 pt-6">
          <div className="flex items-center gap-2 mb-4">
            <FaNewspaper className="text-gray-600" />
            <h3 className="text-lg font-bold text-gray-900">온도에 영향을 준 주요 소식</h3>
          </div>
          <div className="space-y-3 max-h-64 overflow-y-auto">
            {influentialNews && influentialNews.length > 0 ? (
              influentialNews.slice(0, 5).map((news, index) => (
                <motion.div 
                  key={index}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="p-4 bg-gradient-to-r from-gray-50 to-white rounded-xl border border-gray-200 hover:shadow-md transition-all duration-200"
                >
                  <p className="text-sm font-medium text-gray-800 line-clamp-2 mb-2">
                    {news.title}
                  </p>
                  <div className="flex justify-between items-center">
                    <span className="text-xs text-gray-600 bg-gray-100 px-2 py-1 rounded-full">
                      {news.source}
                    </span>
                    {news.view_count && (
                      <span className="text-xs text-gray-500">
                        조회 {news.view_count.toLocaleString()}
                      </span>
                    )}
                  </div>
                </motion.div>
              ))
            ) : (
              Array.from({ length: 5 }).map((_, index) => (
                <div key={index} className="p-4 bg-gradient-to-r from-gray-50 to-white rounded-xl border border-gray-200 animate-pulse">
                  <div className="h-4 bg-gray-200 rounded mb-2"></div>
                  <div className="h-3 bg-gray-200 rounded w-3/4 mb-2"></div>
                  <div className="flex justify-between items-center">
                    <div className="h-3 bg-gray-200 rounded w-16"></div>
                    <div className="h-3 bg-gray-200 rounded w-12"></div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </Modal>
  )
}