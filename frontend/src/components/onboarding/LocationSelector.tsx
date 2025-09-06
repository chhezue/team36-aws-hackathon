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
        if (response.districts) {
          setDistricts(response.districts)
        } else {
          throw new Error('데이터 형식 오류')
        }
      } catch (error) {
        console.error('구 데이터 로드 실패:', error)
        setDistricts([
          '강남구', '강동구', '강북구', '강서구', '관악구', '광진구', '구로구', '금천구',
          '노원구', '도봉구', '동대문구', '동작구', '마포구', '서대문구', '서초구',
          '성동구', '성북구', '송파구', '양천구', '영등포구', '용산구', '은평구',
          '종로구', '중구', '중랑구'
        ])
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
          className="w-full p-4 glass border border-white/20 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-400 focus:border-white/30 text-gray-900 backdrop-blur-16"
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