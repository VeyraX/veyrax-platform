import { UserAuthPage } from '@/app/modules/auth/pages/user-auth-page'
import { Suspense } from 'react'

export default function ProviderAuthPage({ 
  params,
  searchParams
}: { 
  params: { provider_tag: string },
  searchParams: { code?: string, api_key?: string, success?: string, status_code?: string, oauth_return?: string, type?: string }
}) {
  const code = searchParams.code || '';
  const apiKey = searchParams.api_key || '';
  const type = searchParams.type || '';
  
  return (
    <Suspense fallback={
      <div className="min-h-screen flex items-center justify-center bg-white">
        <p className="text-black">Connecting...</p>
      </div>
    }>
      <UserAuthPage 
        providerTag={params.provider_tag} 
        code={code} 
        apiKey={apiKey} 
        type={type}
      />
    </Suspense>
  )
}
