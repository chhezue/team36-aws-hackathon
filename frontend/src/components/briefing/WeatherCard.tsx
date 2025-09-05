import { motion } from 'framer-motion'
import { HiSun } from 'react-icons/hi'
import Card from '../ui/Card'

interface WeatherCardProps {
  condition: string
  temperature: number
  dust: string
  description?: string
}

const getTempColor = (temp: number) => {
  if (temp >= 25) return 'text-error'
  if (temp >= 15) return 'text-warning'
  if (temp >= 5) return 'text-info'
  return 'text-gray-600'
}

const getDustColor = (dust: string) => {
  if (dust === '좋음') return 'text-success'
  if (dust === '보통') return 'text-warning'
  return 'text-error'
}

export default function WeatherCard({ 
  condition, 
  temperature, 
  dust, 
  description
}: WeatherCardProps) {
  return (
    <motion.div 
      initial={{ opacity: 0, y: 30, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ duration: 0.6, ease: "easeOut" }}
      className="animate-glass-appear"
    >
      <Card className="glass-strong border-white/20 hover:border-white/30">
        <div className="flex items-center gap-3 mb-4">
          <HiSun className="text-2xl text-yellow-400 drop-shadow-lg" />
          <h2 className="text-h3 text-gray-900 font-semibold">오늘의 날씨</h2>
        </div>
        <div className="space-y-3">
          <p className={`text-2xl font-bold ${getTempColor(temperature)} drop-shadow`}>
            {condition}, 최고 {temperature}°C
          </p>
          <div className="flex items-center gap-2">
            <span className="text-small text-gray-600">미세먼지</span>
            <span className={`text-small font-medium ${getDustColor(dust)} drop-shadow-sm`}>{dust}</span>
          </div>
          {description && (
            <p className="text-small text-gray-700 glass p-3 rounded-lg border border-white/10">{description}</p>
          )}
        </div>
      </Card>
    </motion.div>
  )
}