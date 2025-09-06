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
      <svg viewBox="0 0 120 40" fill="none" xmlns="http://www.w3.org/2000/svg" className="w-full h-full">
        {/* 온도계 아이콘 */}
        <rect x="8" y="6" width="6" height="16" rx="3" fill="#6366f1" stroke="#4f46e5" strokeWidth="0.8"/>
        <circle cx="11" cy="26" r="3" fill="#ef4444" stroke="#dc2626" strokeWidth="0.8"/>
        
        {/* 온도 표시선들 */}
        <line x1="14" y1="10" x2="16" y2="10" stroke="#4f46e5" strokeWidth="0.8"/>
        <line x1="14" y1="14" x2="17" y2="14" stroke="#4f46e5" strokeWidth="0.8"/>
        <line x1="14" y1="18" x2="16" y2="18" stroke="#4f46e5" strokeWidth="0.8"/>
        
        {/* 감성 파동 */}
        <circle cx="11" cy="20" r="8" fill="none" stroke="#6366f1" strokeWidth="0.5" opacity="0.3"/>
        <circle cx="11" cy="20" r="10" fill="none" stroke="#8b5cf6" strokeWidth="0.3" opacity="0.2"/>
        
        {/* 텍스트 */}
        <text x="25" y="16" fontFamily="Inter, sans-serif" fontSize="12" fontWeight="700" fill="currentColor">Vibe</text>
        <text x="25" y="28" fontFamily="Inter, sans-serif" fontSize="12" fontWeight="700" fill="#6366f1">Thermo</text>
        
        {/* 서브텍스트 */}
        <text x="70" y="20" fontFamily="Inter, sans-serif" fontSize="8" fontWeight="400" fill="#6b7280">감성 온도계</text>
      </svg>
    </div>
  )
}