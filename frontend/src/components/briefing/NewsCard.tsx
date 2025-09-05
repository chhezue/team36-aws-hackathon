import { motion } from 'framer-motion'
import Card from '../ui/Card'

interface NewsItem {
  title: string
  source: string
  sentiment?: string
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

const getSentimentEmoji = (sentiment: string) => {
  switch (sentiment) {
    case 'sunny': return '☀️'
    case 'cloudy': return '⛅'
    case 'rainy': return '🌧️'
    case 'stormy': return '⛈️'
    case 'hot': return '🔥'
    case 'warm': return '🌡️'
    case 'cool': return '❄️'
    case 'cold': return '🧊'
    default: return '📰'
  }
}

export default function NewsCard({ title, IconComponent, items, delay = 0 }: NewsCardProps) {
  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay }}
      className="animate-slide-up"
    >
      <Card>
        <div className="flex items-center gap-3 mb-4">
          <IconComponent className="text-2xl text-primary-500" />
          <h2 className="text-h3 text-gray-900">{title}</h2>
        </div>
        <div className="space-y-3">
          {items.map((item, index) => (
            <div key={index} className="p-4 bg-gray-50 rounded-xl border border-gray-100 hover:bg-gray-100 transition-colors">
              <div className="flex items-start justify-between gap-2">
                <p className="text-body font-medium flex-1 text-gray-900">{item.title}</p>
                {item.sentiment && (
                  <span className="text-lg">{getSentimentEmoji(item.sentiment)}</span>
                )}
              </div>
              <p className="text-small text-gray-600 mt-2">{item.source}</p>
            </div>
          ))}
        </div>
      </Card>
    </motion.div>
  )
}