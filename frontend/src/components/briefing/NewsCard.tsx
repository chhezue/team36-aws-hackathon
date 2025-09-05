import { motion } from 'framer-motion'
import { Eye } from 'lucide-react'
import Card from '../ui/Card'
import { formatViewCount, generateNaverMapUrl } from '@/lib/utils'

interface NewsItem {
  title: string
  source: string
  sentiment?: string
  url?: string
  viewCount?: number
  address?: string
  category?: string
}

interface NewsCardProps {
  title: string
  IconComponent: React.ComponentType<{ className?: string }>
  items: NewsItem[]
  delay?: number
}

const getSentimentColor = (sentiment: string) => {
  switch (sentiment) {
    case 'positive': return 'text-success'
    case 'negative': return 'text-error'
    case 'neutral': return 'text-gray-600'
    default: return 'text-gray-600'
  }
}



export default function NewsCard({ title, IconComponent, items, delay = 0 }: NewsCardProps) {
  return (
    <motion.div 
      initial={{ opacity: 0, y: 30, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ delay, duration: 0.6, ease: "easeOut" }}
      className="animate-glass-appear"
    >
      <Card className="glass-strong border-white/30 hover:border-white/40 shadow-xl">
        <div className="flex items-center gap-4 mb-6">
          <div className="p-2 bg-gradient-to-br from-primary-400 to-primary-600 rounded-xl shadow-lg">
            <IconComponent className="text-xl text-white" />
          </div>
          <h2 className="text-xl font-bold text-gray-800">{title}</h2>
        </div>
        <div className="space-y-4">
          {items.length > 0 ? (
            items.map((item, index) => (
              <div key={index} className="p-5 glass rounded-2xl border border-white/20 hover:glass-strong transition-all duration-300 shadow-lg">
                <div className="flex items-start justify-between gap-3">
                  {item.url ? (
                    <a 
                      href={item.url} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="text-base font-semibold flex-1 text-gray-800 hover:text-primary-600 transition-colors cursor-pointer underline-offset-2 hover:underline leading-snug"
                    >
                      {item.title}
                    </a>
                  ) : item.address ? (
                    <a 
                      href={generateNaverMapUrl(item.title, item.address)} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="text-base font-semibold flex-1 text-gray-800 hover:text-primary-600 transition-colors cursor-pointer underline-offset-2 hover:underline leading-snug"
                    >
                      {item.title}
                    </a>
                  ) : (
                    <p className="text-base font-semibold flex-1 text-gray-800 leading-snug">{item.title}</p>
                  )}
                  {item.viewCount !== undefined && (
                    <span className="text-sm text-gray-600 font-medium whitespace-nowrap flex items-center gap-1.5 bg-white/50 px-2 py-1 rounded-full">
                      <Eye size={14} />
                      {formatViewCount(item.viewCount)}
                    </span>
                  )}
                </div>
                <div className="flex items-center gap-2 mt-3">
                  {item.category && (
                    <span className="text-sm bg-gradient-to-r from-primary-100 to-primary-200 text-primary-800 px-3 py-1 rounded-full font-medium shadow-sm">
                      {item.category}
                    </span>
                  )}
                  <p className="text-sm text-gray-600 font-medium">{item.source}</p>
                </div>
                {item.address && (
                  <p className="text-sm text-gray-500 mt-2 leading-relaxed">{item.address}</p>
                )}
              </div>
            ))
          ) : (
            <div className="space-y-4">
              {[...Array(3)].map((_, index) => (
                <div key={index} className="p-5 glass rounded-2xl border border-white/20 shadow-lg">
                  <div className="animate-pulse">
                    <div className="h-5 bg-white/40 rounded-lg w-3/4 mb-3"></div>
                    <div className="h-4 bg-white/30 rounded-lg w-1/2 mb-2"></div>
                    <div className="h-3 bg-white/20 rounded-lg w-2/3"></div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </Card>
    </motion.div>
  )
}