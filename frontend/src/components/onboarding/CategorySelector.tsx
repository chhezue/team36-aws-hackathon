import { HiSun, HiChat, HiLocationMarker, HiSparkles } from 'react-icons/hi'

interface Category {
  id: string
  name: string
  icon: string
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
            className={`p-4 rounded-xl border-2 cursor-pointer transition-all ${
              isSelected
                ? 'border-primary-500 bg-primary-50 shadow-md'
                : 'border-gray-200 bg-white hover:bg-gray-50'
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