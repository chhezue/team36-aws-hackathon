/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    return [
      {
        source: '/api/lambda/:path*',
        destination: 'https://xn---function-url-9q93cj85godb.lambda-url.us-east-1.on.aws/:path*'
      },
      {
        source: '/api/:path*',
        destination: 'http://localhost:8000/api/:path*'
      }
    ]
  }
}

module.exports = nextConfig