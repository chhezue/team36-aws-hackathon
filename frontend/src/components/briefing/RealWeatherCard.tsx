import { motion } from 'framer-motion'
import { FaSun, FaCloud, FaCloudRain, FaSnowflake } from 'react-icons/fa'
import { WiDaySunny, WiCloudy, WiRain, WiSnow, WiFog } from 'react-icons/wi'
import Card from '../ui/Card'

interface RealWeatherCardProps {
  condition: string
  temp: string
  dust: string
  description?: string
  hourlyForecast?: Array<{
    time: string
    temp: string
    condition: string
  }>
}

const getWeatherIcon = (condition: string) => {
  if (condition.includes('맑음')) return <WiDaySunny className="text-yellow-500" />
  if (condition.includes('구름')) return <WiCloudy className="text-gray-500" />
  if (condition.includes('흐림')) return <WiFog className="text-gray-600" />
  if (condition.includes('비')) return <WiRain className="text-blue-500" />
  if (condition.includes('눈')) return <WiSnow className="text-blue-200" />
  return <WiDaySunny className="text-yellow-500" />
}

const getDustColor = (dust: string) => {
  if (dust === '좋음') return 'text-green-600'
  if (dust === '보통') return 'text-yellow-600'
  return 'text-red-600'
}

export default function RealWeatherCard({ 
  condition, 
  temp, 
  dust, 
  description,
  hourlyForecast
}: RealWeatherCardProps) {
  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="animate-slide-up"
    >
      <Card className="bg-gradient-to-br from-blue-50 to-sky-50 border-blue-100">
        <div className="flex items-center gap-3 mb-4">
          <FaSun className="text-2xl text-blue-500" />
          <h2 className="text-h3 text-gray-900">진짜 오늘의 날씨</h2>
        </div>
        <div className="space-y-4">
          <div className="flex items-center gap-3">
            <div className="text-3xl">{getWeatherIcon(condition)}</div>
            <div>
              <p className="text-2xl font-bold text-gray-900">
                {condition}, {temp}
              </p>
              <div className="flex items-center gap-2 mt-1">
                <span className="text-small text-gray-600">미세먼지</span>
                <span className={`text-small font-medium ${getDustColor(dust)}`}>{dust}</span>
              </div>
            </div>
          </div>
          
          {hourlyForecast && hourlyForecast.length > 0 && (
            <div className="bg-white/50 p-3 rounded-lg">
              <p className="text-small text-gray-600 mb-2">시간별 예보</p>
              <div className="flex gap-4">
                {hourlyForecast.slice(0, 3).map((forecast, index) => (
                  <div key={index} className="text-center">
                    <p className="text-xs text-gray-500">{forecast.time}</p>
                    <div className="text-lg">{getWeatherIcon(forecast.condition)}</div>
                    <p className="text-xs font-medium">{forecast.temp}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
          
          {description && (
            <p className="text-small text-gray-700 bg-white/50 p-3 rounded-lg">{description}</p>
          )}
        </div>
      </Card>
    </motion.div>
  )
}