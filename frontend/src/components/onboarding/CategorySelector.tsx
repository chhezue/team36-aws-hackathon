import { HiSun, HiChat, HiLocationMarker, HiSparkles } from 'react-icons/hi'
import { FaUtensils } from 'react-icons/fa'

interface Category {
  id: string
  name: string
}

interface CategorySelectorProps {
  categories: Category[]
  selectedCategories: string[]
  onToggle: (categoryId: string) => void
  onSelectAll: () => void
}

const getIconForCategory = (categoryId: string) => {
  switch (categoryId) {
    case 'weather': return <HiSun className="text-yellow-500" />
    case 'community': return <HiChat className="text-blue-500" />
    case 'new_restaurants': return <HiSparkles className="text-pink-500" />
    case 'hot_restaurants': return <FaUtensils className="text-orange-500" />
    case 'restaurants': return <FaUtensils className="text-orange-500" />
    default: return <HiLocationMarker className="text-green-500" />
  }
}

export default function CategorySelector({ 
  categories, 
  selectedCategories, 
  onToggle, 
  onSelectAll 
}: CategorySelectorProps) {
  return (
    <div className="space-y-4">
      {categories.map(category => {
        const isSelected = selectedCategories.includes(category.id)
        
        return (
          <div
            key={category.id}
            onClick={() => onToggle(category.id)}
            className={`p-5 rounded-2xl border-2 cursor-pointer transition-all duration-300 hover:scale-[1.02] ${
              isSelected
                ? 'border-primary-400/50 glass-strong shadow-xl bg-gradient-to-r from-primary-50/20 to-purple-50/20'
                : 'border-white/20 glass hover:glass-strong hover:border-white/40'
            }`}
          >
            <div className="flex items-center gap-4">
              <div className={`p-3 rounded-xl shadow-lg transition-all duration-300 ${
                isSelected 
                  ? 'bg-gradient-to-br from-primary-400 to-primary-600 scale-110' 
                  : 'bg-white/20 hover:bg-white/30'
              }`}>
                <div className={`text-xl ${isSelected ? 'text-white' : ''}`}>
                  {getIconForCategory(category.id)}
                </div>
              </div>
              <span className="text-lg font-semibold text-gray-900 flex-1">{category.name}</span>
              {isSelected && (
                <div className="w-6 h-6 bg-gradient-to-br from-green-400 to-green-600 rounded-full flex items-center justify-center shadow-lg">
                  <span className="text-white text-sm font-bold">✓</span>
                </div>
              )}
            </div>
          </div>
        )
      })}
      
      <button 
        onClick={onSelectAll}
        className="w-full mt-6 py-4 px-6 bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 text-white font-bold text-lg rounded-2xl shadow-xl hover:shadow-2xl hover:scale-105 transition-all duration-300 border-0"
      >
        <span className="flex items-center justify-center gap-2">
          <HiSparkles className="text-xl" />
          모두 선택
          <HiSparkles className="text-xl" />
        </span>
      </button>
    </div>
  )
}