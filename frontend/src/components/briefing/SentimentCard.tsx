import { motion } from 'framer-motion'
import { FaHeart } from 'react-icons/fa'
import Card from '../ui/Card'

interface SentimentCardProps {
  temperature: number
  moodEmoji: string
  description: string
  onClick?: () => void
}

const getTempColor = (temp: number) => {
  if (temp >= 70) return 'text-red-500'
  if (temp >= 50) return 'text-yellow-500'
  if (temp >= 30) return 'text-blue-500'
  return 'text-gray-500'
}

export default function SentimentCard({ 
  temperature, 
  moodEmoji, 
  description,
  onClick
}: SentimentCardProps) {
  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="animate-slide-up cursor-pointer"
      onClick={onClick}
    >
      <Card className="bg-gradient-to-br from-pink-50 to-rose-50 border-pink-100 hover:shadow-lg transition-shadow">
        <div className="flex items-center gap-3 mb-4">
          <FaHeart className="text-2xl text-pink-500" />
          <h2 className="text-h3 text-gray-900">우리 구의 감성 온도계</h2>
        </div>
        <div className="space-y-3">
          <div className="flex items-center gap-3">
            <span className="text-3xl">{moodEmoji}</span>
            <span className={`text-2xl font-bold ${getTempColor(temperature)}`}>
              {temperature}°C
            </span>
          </div>
          <p className="text-small text-gray-700 bg-white/50 p-3 rounded-lg">
            오늘 우리 동네 분위기는 <strong>{description}</strong>이에요
          </p>
        </div>
      </Card>
    </motion.div>
  )
}