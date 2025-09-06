import { HiSun, HiChat, HiLocationMarker, HiSparkles } from 'react-icons/hi'

interface Category {
  id: string
  name: string
  icon?: string
}

interface CategorySelectorProps {
  categories: Category[]
  selectedCategories: string[]
  onToggle: (categoryId: string) => void
  onSelectAll: () => void
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
            className={`p-4 rounded-xl border-2 cursor-pointer transition-all duration-300 ${
              isSelected
                ? 'border-primary-400/50 glass-strong shadow-lg'
                : 'border-white/20 glass hover:glass-strong'
            }`}
          >
            <div className="flex items-center gap-3">
              <div className="text-2xl text-primary-500">
                {category.id === 'weather' && <HiSun />}
                {category.id === 'community' && <HiChat />}
                {category.id === 'restaurants' && <HiLocationMarker />}
                {category.id === 'new_restaurants' && <HiSparkles />}
              </div>
              <span className="text-body font-medium text-gray-900">{category.name}</span>
              {isSelected && (
                <span className="ml-auto text-lg text-primary-500">✓</span>
              )}
            </div>
          </div>
        )
      })}
      
      <button 
        onClick={onSelectAll}
        className="w-full btn-secondary mt-4"
      >
        모두 선택
      </button>
    </div>
  )
}