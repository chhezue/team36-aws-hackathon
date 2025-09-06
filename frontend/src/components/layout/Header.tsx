import { IoSettings, IoArrowBack } from 'react-icons/io5'

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
  return (
    <div className="flex justify-between items-start mb-10">
      <div className="flex items-center gap-4">
        {showBack && (
          <button 
            onClick={onBack}
            className="p-3 glass-header rounded-xl hover:scale-110 transition-all duration-300 shadow-lg"
          >
            <IoArrowBack size={20} className="text-white drop-shadow" />
          </button>
        )}
        <div>
          <h1 className="text-2xl font-bold text-white drop-shadow-lg mb-1">{title}</h1>
          {subtitle && (
            <p className="text-sm text-white/80 whitespace-pre-line drop-shadow leading-relaxed">{subtitle}</p>
          )}
        </div>
      </div>
      
      <div className="flex gap-2">
        {showSentiment && (
          <button 
            onClick={onSentiment}
            className="p-3 glass-header rounded-xl hover:scale-110 transition-all duration-300 shadow-lg"
            title="동네 분위기 보기"
          >
            <span className="text-lg drop-shadow">🌡️</span>
          </button>
        )}
        {showSettings && (
          <button 
            onClick={onSettings}
            className="p-3 glass-header rounded-xl hover:scale-110 transition-all duration-300 shadow-lg"
            title="설정"
          >
            <IoSettings size={20} className="text-white drop-shadow" />
          </button>
        )}
      </div>
    </div>
  )
}