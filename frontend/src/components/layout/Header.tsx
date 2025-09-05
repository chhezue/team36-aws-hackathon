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
    <div className="flex justify-between items-center mb-8">
      <div className="flex items-center gap-4">
        {showBack && (
          <button 
            onClick={onBack}
            className="p-3 glass rounded-xl shadow-sm border border-gray-200 hover:shadow-md transition-all"
          >
            <IoArrowBack size={20} className="text-gray-600" />
          </button>
        )}
        <div>
          <h1 className="text-h2 text-gray-900">{title}</h1>
          {subtitle && (
            <p className="text-small text-gray-600 whitespace-pre-line mt-1">{subtitle}</p>
          )}
        </div>
      </div>
      
      <div className="flex gap-2">
        {showSentiment && (
          <button 
            onClick={onSentiment}
            className="p-3 glass rounded-xl shadow-sm border border-gray-200 hover:shadow-md transition-all"
            title="동네 분위기 보기"
          >
            <span className="text-lg">🌡️</span>
          </button>
        )}
        {showSettings && (
          <button 
            onClick={onSettings}
            className="p-3 glass rounded-xl shadow-sm border border-gray-200 hover:shadow-md transition-all"
            title="설정"
          >
            <IoSettings size={20} className="text-gray-600" />
          </button>
        )}
      </div>
    </div>
  )
}