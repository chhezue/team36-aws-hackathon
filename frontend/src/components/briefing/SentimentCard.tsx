import { motion } from 'framer-motion'
import { HiSparkles } from 'react-icons/hi'
import { FaThermometerHalf } from 'react-icons/fa'
import Card from '../ui/Card'

interface SentimentCardProps {
  temperature: number
  moodEmoji: string
  description: string
  onClick?: () => void
}

const getTempGradient = (temp: number) => {
  if (temp >= 80) return 'from-red-400 via-red-500 to-red-600'
  if (temp >= 60) return 'from-orange-400 via-orange-500 to-orange-600'
  if (temp >= 40) return 'from-yellow-400 via-yellow-500 to-yellow-600'
  if (temp >= 20) return 'from-blue-400 via-blue-500 to-blue-600'
  return 'from-gray-400 via-gray-500 to-gray-600'
}

const getTempBg = (temp: number) => {
  if (temp >= 80) return 'bg-gradient-to-br from-red-50 to-red-100'
  if (temp >= 60) return 'bg-gradient-to-br from-orange-50 to-orange-100'
  if (temp >= 40) return 'bg-gradient-to-br from-yellow-50 to-yellow-100'
  if (temp >= 20) return 'bg-gradient-to-br from-blue-50 to-blue-100'
  return 'bg-gradient-to-br from-gray-50 to-gray-100'
}

export default function SentimentCard({ 
  temperature, 
  moodEmoji, 
  description,
  onClick
}: SentimentCardProps) {
  return (
    <motion.div 
      initial={{ opacity: 0, y: 30, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ duration: 0.6, ease: "easeOut" }}
      className="animate-glass-appear cursor-pointer"
      onClick={onClick}
    >
      <div className="relative overflow-hidden rounded-3xl">
        {/* 배경 그라데이션 */}
        <div className={`absolute inset-0 bg-gradient-to-br ${getTempGradient(temperature)} opacity-10`} />
        
        <Card className="glass-card rounded-3xl shadow-2xl hover:scale-[1.02] transition-all duration-300 relative">
          {/* 헤더 */}
          <div className="flex items-center justify-between mb-8">
            <div className="flex items-center gap-3">
              <div className={`p-3 bg-gradient-to-br ${getTempGradient(temperature)} rounded-2xl shadow-lg`}>
                <FaThermometerHalf className="text-xl text-white" />
              </div>
              <div>
                <h2 className="text-lg font-bold text-gray-900">감성 온도계</h2>
                <p className="text-xs text-gray-600">우리 동네 분위기</p>
              </div>
            </div>
            <HiSparkles className="text-2xl text-yellow-400 animate-pulse" />
          </div>

          {/* 메인 컨텐츠 */}
          <div className="text-center space-y-6">
            {/* 온도 디스플레이 */}
            <div className="relative">
              <div className={`inline-flex items-center justify-center w-32 h-32 rounded-full ${getTempBg(temperature)} border-4 border-white shadow-xl`}>
                <div className="text-center">
                  <div className="text-5xl mb-2">{moodEmoji}</div>
                  <div className={`text-3xl font-black bg-gradient-to-r ${getTempGradient(temperature)} bg-clip-text text-transparent`}>
                    {temperature}°
                  </div>
                </div>
              </div>
              
              {/* 온도 바 */}
              <div className="mt-4 mx-auto w-24 h-2 bg-gray-200 rounded-full overflow-hidden">
                <div 
                  className={`h-full bg-gradient-to-r ${getTempGradient(temperature)} rounded-full transition-all duration-1000`}
                  style={{ width: `${Math.min(temperature, 100)}%` }}
                />
              </div>
            </div>

            {/* 설명 */}
            <div className="glass-card p-5 rounded-2xl border border-white/30">
              <p className="text-base text-gray-800 leading-relaxed font-medium">
                오늘 우리 동네는 
                <span className={`font-bold bg-gradient-to-r ${getTempGradient(temperature)} bg-clip-text text-transparent ml-1`}>
                  {description}
                </span>
                에요 ✨
              </p>
            </div>
          </div>
        </Card>
      </div>
    </motion.div>
  )
}