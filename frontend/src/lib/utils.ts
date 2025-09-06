/**
 * 조회수를 한국어 형식으로 포맷팅
 * @param count 조회수
 * @returns 포맷팅된 조회수 문자열
 */
export function formatViewCount(count: number): string {
  if (count >= 100000000) {
    return `${(count / 100000000).toFixed(1)}억회`
  } else if (count >= 10000) {
    const manCount = count / 10000
    return manCount % 1 === 0 ? `${manCount}만회` : `${manCount.toFixed(1)}만회`
  } else if (count >= 1000) {
    const thousandCount = count / 1000
    return thousandCount % 1 === 0 ? `${thousandCount}천회` : `${thousandCount.toFixed(1)}천회`
  } else {
    return `${count}회`
  }
}

/**
 * 네이버 지도 검색 URL 생성
 * @param name 음식점 이름
 * @param address 주소
 * @returns 네이버 지도 URL
 */
export function generateNaverMapUrl(name: string, address?: string): string {
  const query = address || name
  return `https://map.naver.com/v5/search/${encodeURIComponent(query)}`
}