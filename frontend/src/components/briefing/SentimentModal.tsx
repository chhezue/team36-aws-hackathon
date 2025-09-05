import Modal from '../ui/Modal'

interface SentimentModalProps {
  isOpen: boolean
  onClose: () => void
  sentiment: {
    positiveRatio: number
    negativeRatio: number
    moodEmoji: string
  }
}

const getWeatherDescription = (positiveRatio: number, negativeRatio: number) => {
  if (positiveRatio > 70) return { text: '맑은 날씨', emoji: '☀️', color: 'weather-sunny' }
  if (positiveRatio > 50) return { text: '따뜻한 날씨', emoji: '🌤️', color: 'temp-warm' }
  if (negativeRatio > 50) return { text: '흐린 날씨', emoji: '⛅', color: 'weather-cloudy' }
  if (negativeRatio > 70) return { text: '비오는 날씨', emoji: '🌧️', color: 'weather-rainy' }
  return { text: '보통 날씨', emoji: '⛅', color: 'weather-cloudy' }
}

export default function SentimentModal({ isOpen, onClose, sentiment }: SentimentModalProps) {
  const weather = getWeatherDescription(sentiment.positiveRatio, sentiment.negativeRatio)
  
  return (
    <Modal isOpen={isOpen} onClose={onClose} title="동네 날씨">
      <div className="text-center space-y-6">
        <div className="text-6xl">{weather.emoji}</div>
        <p className={`text-xl font-bold ${weather.color}`}>
          오늘 동네는 {weather.text}예요
        </p>
        
        <div className="space-y-4">
          <div className="flex justify-between items-center">
            <div className="flex items-center gap-2">
              <span className="text-lg">☀️</span>
              <span className="text-sm font-medium">맑음</span>
            </div>
            <span className="text-sm font-bold weather-sunny">{sentiment.positiveRatio}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-3">
            <div 
              className="h-3 rounded-full transition-all duration-500"
              style={{
                width: `${sentiment.positiveRatio}%`,
                background: 'linear-gradient(90deg, var(--sunny) 0%, var(--warm) 100%)'
              }}
            />
          </div>
          
          <div className="flex justify-between items-center">
            <div className="flex items-center gap-2">
              <span className="text-lg">🌧️</span>
              <span className="text-sm font-medium">비</span>
            </div>
            <span className="text-sm font-bold weather-rainy">{sentiment.negativeRatio}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-3">
            <div 
              className="h-3 rounded-full transition-all duration-500"
              style={{
                width: `${sentiment.negativeRatio}%`,
                background: 'linear-gradient(90deg, var(--rainy) 0%, var(--stormy) 100%)'
              }}
            />
          </div>
        </div>
        
        <p className="text-sm text-text-secondary">
          동네 소식을 분석한 결과입니다
        </p>
      </div>
    </Modal>
  )
}