interface CardProps {
  children: React.ReactNode
  className?: string
  onClick?: () => void
  variant?: 'default' | 'glass' | 'solid'
}

export default function Card({ 
  children, 
  className = '', 
  onClick,
  variant = 'default'
}: CardProps) {
  const variantClasses = {
    default: 'glass-card',
    glass: 'glass-strong',
    solid: 'bg-white shadow-xl border border-gray-200'
  }

  return (
    <div 
      className={`
        p-6 rounded-2xl transition-all duration-300
        ${variantClasses[variant]}
        ${onClick ? 'cursor-pointer hover:scale-[1.02]' : ''}
        ${className}
      `}
      onClick={onClick}
    >
      {children}
    </div>
  )
}