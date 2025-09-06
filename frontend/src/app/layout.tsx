import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'VibeThermo',
  description: '우리 동네 감성 온도를 매일 아침 체크하세요',
  icons: {
    icon: '/favicon.svg',
    shortcut: '/favicon.ico',
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="ko" className="scroll-smooth">
      <body className="min-h-screen text-gray-900 antialiased">
        <div className="container mx-auto max-w-md px-4 relative z-10">
          {children}
        </div>
      </body>
    </html>
  )
}