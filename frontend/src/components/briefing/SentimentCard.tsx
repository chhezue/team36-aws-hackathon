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
      initial={{ opacity: 0, y: 30, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ duration: 0.6, ease: "easeOut" }}
      className="animate-glass-appear cursor-pointer"
      onClick={onClick}
    >
      <Card className="glass-strong border-white/20 hover:border-white/30 hover:glass-modal transition-all duration-300">
        <div className="flex items-center gap-3 mb-4">
          <FaHeart className="text-2xl text-pink-400 drop-shadow-lg" />
          <h2 className="text-h3 text-gray-900 font-semibold">우리 구의 감성 온도계</h2>
        </div>
        <div className="space-y-3">
          <div className="flex items-center gap-3">
            <span className="text-3xl drop-shadow-lg">{moodEmoji}</span>
            <span className={`text-2xl font-bold ${getTempColor(temperature)} drop-shadow`}>
              {temperature}°C
            </span>
          </div>
          <p className="text-small text-gray-700 glass p-3 rounded-lg border border-white/10">
            오늘 우리 동네 분위기는 <strong>{description}</strong>이에요
          </p>
        </div>
      </Card>
    </motion.div>
  )
}