export const env = {
  API_URL: process.env.NEXT_PUBLIC_API_URL || 'https://connect-aitu.me/api',
  APP_URL: process.env.NEXT_PUBLIC_APP_URL || 'https://connect-aitu.me',
} as const;