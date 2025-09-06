import { motion } from 'framer-motion'
import { WiDaySunny, WiCloudy, WiRain, WiSnow, WiFog, WiThermometer } from 'react-icons/wi'
import { FiWind } from 'react-icons/fi'
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
  if (condition.includes('맑음')) return <WiDaySunny className="text-yellow-400" />
  if (condition.includes('구름')) return <WiCloudy className="text-gray-400" />
  if (condition.includes('흐림')) return <WiFog className="text-gray-500" />
  if (condition.includes('비')) return <WiRain className="text-blue-400" />
  if (condition.includes('눈')) return <WiSnow className="text-blue-300" />
  return <WiDaySunny className="text-yellow-400" />
}

const getDustColor = (dust: string) => {
  if (dust === '좋음') return 'bg-green-100 text-green-700 border-green-200'
  if (dust === '보통') return 'bg-yellow-100 text-yellow-700 border-yellow-200'
  return 'bg-red-100 text-red-700 border-red-200'
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
      initial={{ opacity: 0, y: 30, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ duration: 0.6, ease: "easeOut" }}
      className="animate-glass-appear"
    >
      <Card className="glass-card rounded-3xl shadow-2xl">
        <div className="flex items-center gap-4 mb-6">
          <div className="p-2 bg-gradient-to-br from-blue-400 to-blue-600 rounded-xl shadow-lg">
            <WiThermometer className="text-xl text-white" />
          </div>
          <h2 className="text-xl font-bold text-gray-800">오늘의 날씨</h2>
        </div>
        
        <div className="space-y-6">
          {/* 메인 날씨 정보 */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="text-5xl drop-shadow-lg">{getWeatherIcon(condition)}</div>
              <div>
                <p className="text-3xl font-bold text-gray-900 mb-1">{temp}</p>
                <p className="text-lg text-gray-700 font-medium">{condition}</p>
              </div>
            </div>
          </div>
          
          {/* 미세먼지 정보 */}
          <div className="flex items-center gap-3">
            <FiWind className="text-lg text-gray-500" />
            <span className="text-sm text-gray-700 font-medium">미세먼지</span>
            <span className={`px-3 py-1 rounded-full text-xs font-bold border ${getDustColor(dust)}`}>
              {dust}
            </span>
          </div>
          
          {/* 시간별 예보 */}
          {hourlyForecast && hourlyForecast.length > 0 && (
            <div className="glass-card p-4 rounded-2xl">
              <p className="text-sm font-bold text-gray-800 mb-3">시간별 예보</p>
              <div className="flex justify-between">
                {hourlyForecast.slice(0, 4).map((forecast, index) => (
                  <div key={index} className="text-center flex-1">
                    <p className="text-xs text-gray-600 font-medium mb-2">{forecast.time}</p>
                    <div className="text-2xl mb-2 flex justify-center">{getWeatherIcon(forecast.condition)}</div>
                    <p className="text-sm font-bold text-gray-900">{forecast.temp}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
          
          {/* 설명 */}
          {description && (
            <div className="glass-card p-4 rounded-2xl">
              <p className="text-sm text-gray-800 leading-relaxed font-medium">{description}</p>
            </div>
          )}
        </div>
      </Card>
    </motion.div>
  )
}