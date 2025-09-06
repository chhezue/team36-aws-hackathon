interface LogoProps {
  size?: 'sm' | 'md' | 'lg'
  className?: string
}

export default function Logo({ size = 'md', className = '' }: LogoProps) {
  const sizeClasses = {
    sm: 'w-20 h-8',
    md: 'w-24 h-10', 
    lg: 'w-32 h-12'
  }

  return (
    <div className={`${sizeClasses[size]} ${className}`}>
      <svg viewBox="0 0 140 48" fill="none" xmlns="http://www.w3.org/2000/svg" className="w-full h-full">
        <defs>
          <linearGradient id="thermoBg" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#667eea" stopOpacity="0.1"/>
            <stop offset="100%" stopColor="#764ba2" stopOpacity="0.1"/>
          </linearGradient>
          <linearGradient id="thermoGrad" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#8b5cf6"/>
            <stop offset="50%" stopColor="#6366f1"/>
            <stop offset="100%" stopColor="#4f46e5"/>
          </linearGradient>
          <linearGradient id="tempGrad" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#f59e0b"/>
            <stop offset="100%" stopColor="#ef4444"/>
          </linearGradient>
        </defs>
        
        <rect width="140" height="48" rx="12" fill="url(#thermoBg)" stroke="rgba(255,255,255,0.2)" strokeWidth="1"/>
        <rect x="10" y="8" width="8" height="20" rx="4" fill="url(#thermoGrad)" stroke="rgba(255,255,255,0.3)" strokeWidth="1"/>
        <circle cx="14" cy="32" r="4" fill="url(#tempGrad)" stroke="rgba(255,255,255,0.3)" strokeWidth="1"/>
        
        <line x1="18" y1="12" x2="21" y2="12" stroke="#8b5cf6" strokeWidth="1.5" strokeLinecap="round"/>
        <line x1="18" y1="16" x2="22" y2="16" stroke="#6366f1" strokeWidth="1.5" strokeLinecap="round"/>
        <line x1="18" y1="20" x2="21" y2="20" stroke="#4f46e5" strokeWidth="1.5" strokeLinecap="round"/>
        <line x1="18" y1="24" x2="22" y2="24" stroke="#3730a3" strokeWidth="1.5" strokeLinecap="round"/>
        
        <circle cx="14" cy="24" r="10" fill="none" stroke="#8b5cf6" strokeWidth="1" opacity="0.4"/>
        <circle cx="14" cy="24" r="12" fill="none" stroke="#a855f7" strokeWidth="0.8" opacity="0.3"/>
        <circle cx="14" cy="24" r="14" fill="none" stroke="#c084fc" strokeWidth="0.6" opacity="0.2"/>
        
        <text x="32" y="20" fontFamily="Inter, sans-serif" fontSize="16" fontWeight="800" fill="currentColor">Vibe</text>
        <text x="32" y="34" fontFamily="Inter, sans-serif" fontSize="16" fontWeight="800" fill="#6366f1">Thermo</text>
        <text x="85" y="26" fontFamily="Inter, sans-serif" fontSize="10" fontWeight="500" fill="#6b7280">감성 온도계</text>
        
        <path d="M120 20c-1-1.5-3-1.5-3 0.5s2 2.5 3 4c1-1.5 3-2.5 3-4s-2-2-3-0.5z" fill="#f59e0b" opacity="0.8"/>
        <circle cx="14" cy="32" r="4" fill="none" stroke="#ef4444" strokeWidth="0.5" opacity="0.6"/>
        <circle cx="14" cy="32" r="5" fill="none" stroke="#f59e0b" strokeWidth="0.3" opacity="0.4"/>
      </svg>
    </div>
  )
}