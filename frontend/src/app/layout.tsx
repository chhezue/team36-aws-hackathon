import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'LocalBriefing',
  description: '우리 동네 소식을 매일 아침 받아보세요',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="ko" className="scroll-smooth">
      <body className="min-h-screen bg-white text-gray-900 antialiased">
        <div className="container mx-auto max-w-md px-4">
          {children}
        </div>
      </body>
    </html>
  )
}