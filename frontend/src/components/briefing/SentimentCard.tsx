import { motion } from 'framer-motion'
import { HiSparkles, HiInformationCircle } from 'react-icons/hi'
import { FaThermometerHalf } from 'react-icons/fa'
import { useState } from 'react'
import Card from '../ui/Card'

interface NewsItem {
  title: string
  source: string
  url?: string
  view_count?: number
}

interface SentimentCardProps {
  temperature: number
  moodEmoji: string
  description: string
  influentialNews?: NewsItem[]
  onClick?: () => void
}

const getTempGradient = (temp: number) => {
  if (temp >= 80) return 'from-rose-500 via-pink-500 to-red-500'
  if (temp >= 60) return 'from-amber-400 via-orange-400 to-red-400'
  if (temp >= 40) return 'from-emerald-400 via-teal-400 to-cyan-400'
  if (temp >= 20) return 'from-blue-500 via-indigo-500 to-purple-500'
  return 'from-slate-400 via-gray-500 to-zinc-500'
}

const getTempBg = (temp: number) => {
  if (temp >= 80) return 'bg-gradient-to-br from-rose-50/80 via-pink-50/60 to-red-50/80'
  if (temp >= 60) return 'bg-gradient-to-br from-amber-50/80 via-orange-50/60 to-red-50/80'
  if (temp >= 40) return 'bg-gradient-to-br from-emerald-50/80 via-teal-50/60 to-cyan-50/80'
  if (temp >= 20) return 'bg-gradient-to-br from-blue-50/80 via-indigo-50/60 to-purple-50/80'
  return 'bg-gradient-to-br from-slate-50/80 via-gray-50/60 to-zinc-50/80'
}

export default function SentimentCard({ 
  temperature, 
  moodEmoji, 
  description,
  influentialNews = [],
  onClick
}: SentimentCardProps) {
  const [showTooltip, setShowTooltip] = useState(false)
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
        <div className={`absolute inset-0 bg-gradient-to-br ${getTempGradient(temperature)} opacity-8`} />
        <div className="absolute inset-0 bg-gradient-to-t from-white/20 via-transparent to-white/10" />
        
        <Card className="glass-card rounded-3xl shadow-2xl hover:scale-[1.02] transition-all duration-300 relative">
          {/* 헤더 */}
          <div className="flex items-center justify-between mb-8">
            <div className="flex items-center gap-3">
              <div className={`p-3 bg-gradient-to-br ${getTempGradient(temperature)} rounded-2xl shadow-lg`}>
                <FaThermometerHalf className="text-xl text-white" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h2 className="text-lg font-bold text-gray-900">감성 온도계</h2>
                  <div className="relative">
                    {showTooltip && influentialNews.length > 0 && (
                      <div className="absolute top-6 left-0 z-50 w-80 p-4 glass-modal rounded-xl border border-white/30 shadow-2xl">
                        <h4 className="text-sm font-bold text-gray-900 mb-3">온도에 영향을 준 주요 소식</h4>
                        <div className="space-y-2 max-h-48 overflow-y-auto">
                          {influentialNews.slice(0, 5).map((news, index) => (
                            <div key={index} className="p-2 glass rounded-lg border border-white/20">
                              <p className="text-xs font-medium text-gray-800 line-clamp-2 mb-1">
                                {news.title}
                              </p>
                              <div className="flex justify-between items-center">
                                <span className="text-xs text-gray-600">{news.source}</span>
                                {news.view_count && (
                                  <span className="text-xs text-gray-500">
                                    조회 {news.view_count.toLocaleString()}
                                  </span>
                                )}
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
                <p className="text-xs text-gray-600">우리 동네 분위기</p>
              </div>
            </div>
          </div>

          {/* 메인 컨텐츠 */}
          <div className="text-center space-y-6">
            {/* 온도 디스플레이 */}
            <div className="relative">
              <div className={`inline-flex items-center justify-center w-32 h-32 rounded-full ${getTempBg(temperature)} border-4 border-white/90 shadow-2xl backdrop-blur-sm`}>
                <div className="text-center">
                  <div className="text-5xl mb-2">{moodEmoji}</div>
                  <div className={`text-3xl font-black bg-gradient-to-r ${getTempGradient(temperature)} bg-clip-text text-transparent`}>
                    {temperature}°
                  </div>
                </div>
              </div>
              
              {/* 온도 바 */}
              <div className="mt-4 mx-auto w-24 h-2 bg-white/40 rounded-full overflow-hidden shadow-inner">
                <div 
                  className={`h-full bg-gradient-to-r ${getTempGradient(temperature)} rounded-full transition-all duration-1000 shadow-sm`}
                  style={{ width: `${Math.min(temperature, 100)}%` }}
                />
              </div>
            </div>

            {/* 설명 */}
            <div className="glass-card p-5 rounded-2xl border border-white/40 bg-white/10">
              <p className="text-base text-gray-800 leading-relaxed font-medium">
                오늘 우리 동네는 
                <span className={`font-bold bg-gradient-to-r ${getTempGradient(temperature)} bg-clip-text text-transparent ml-1 drop-shadow-sm`}>
                  {description}
                </span>
                이에요.
              </p>
            </div>
          </div>
        </Card>
      </div>
    </motion.div>
  )
}