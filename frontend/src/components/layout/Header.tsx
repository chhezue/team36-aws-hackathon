import { IoSettings, IoArrowBack } from 'react-icons/io5'
import { HiLocationMarker, HiCalendar } from 'react-icons/hi'
import { FaThermometerHalf } from 'react-icons/fa'

interface HeaderProps {
  title: string
  subtitle?: string
  showBack?: boolean
  showSettings?: boolean
  showSentiment?: boolean
  onBack?: () => void
  onSettings?: () => void
  onSentiment?: () => void
}

export default function Header({ 
  title, 
  subtitle, 
  showBack, 
  showSettings, 
  showSentiment,
  onBack, 
  onSettings,
  onSentiment 
}: HeaderProps) {
  const subtitleLines = subtitle?.split('\n') || []
  const location = subtitleLines[0]?.replace('📍 ', '') || ''
  const date = subtitleLines[1] || ''

  return (
    <div className="mb-8">
      {/* 상단 네비게이션 */}
      <div className="flex justify-between items-center mb-6">
        <div className="flex items-center gap-3">
          {showBack && (
            <button 
              onClick={onBack}
              className="p-3 glass-header rounded-xl hover:scale-110 transition-all duration-300 shadow-lg"
            >
              <IoArrowBack size={20} className="text-white drop-shadow" />
            </button>
          )}
          <div className="flex items-center gap-2">
            <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-pink-500 rounded-xl flex items-center justify-center shadow-lg">
              <FaThermometerHalf className="text-white text-lg" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-white drop-shadow-lg">VibeThermo</h1>
              <p className="text-xs text-white/70">감성 온도계</p>
            </div>
          </div>
        </div>
        
        <button 
          onClick={onSettings}
          className="p-3 glass-header rounded-xl hover:scale-110 transition-all duration-300 shadow-lg"
        >
          <IoSettings size={20} className="text-white drop-shadow" />
        </button>
      </div>

      {/* 위치 및 날짜 정보 */}
      <div className="glass-card rounded-2xl p-4 border border-white/20">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <HiLocationMarker className="text-white text-lg" />
            <span className="text-white font-medium">{location}</span>
          </div>
          <div className="flex items-center gap-2">
            <HiCalendar className="text-white text-sm" />
            <span className="text-white/80 text-sm">{date}</span>
          </div>
        </div>
      </div>
    </div>
  )
}