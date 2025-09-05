import { useState, useEffect } from 'react'
import { api } from '@/lib/api'
import Skeleton from '@/components/ui/Skeleton'

interface LocationSelectorProps {
  selectedGu: string
  onSelect: (gu: string) => void
}

export default function LocationSelector({ selectedGu, onSelect }: LocationSelectorProps) {
  const [districts, setDistricts] = useState<string[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchDistricts = async () => {
      try {
        const response = await api.getDistricts()
        if (response.success && response.districts) {
          // 데이터가 있는 구만 표시
          const availableDistricts = response.districts
            .filter((district: any) => district.has_data)
            .map((district: any) => district.name)
          setDistricts(availableDistricts.length > 0 ? availableDistricts : response.districts.map((d: any) => d.name))
        } else {
          throw new Error('데이터 형식 오류')
        }
      } catch (error) {
        console.error('구 데이터 로드 실패:', error)
        setDistricts(['강남구', '강동구', '강북구']) // fallback
      } finally {
        setLoading(false)
      }
    }
    fetchDistricts()
  }, [])

  return (
    <div className="space-y-4">
      <label className="block text-sm font-medium">구 선택</label>
      {loading ? (
        <Skeleton className="w-full h-14 rounded-xl" />
      ) : (
        <select 
          value={selectedGu}
          onChange={(e) => onSelect(e.target.value)}
          className="w-full p-4 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary"
        >
          <option value="">구를 선택하세요</option>
          {districts.map(district => (
            <option key={district} value={district}>{district}</option>
          ))}
        </select>
      )}
    </div>
  )
}