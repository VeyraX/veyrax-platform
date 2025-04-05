import { UserAuthPage } from '@/app/modules/auth/pages/user-auth-page'
import { Suspense } from 'react'

export default function ProviderAuthPage({ 
  params,
  searchParams
}: { 
  params: { provider_tag: string },
  searchParams: { code?: string }
}) {
  const code = searchParams.code || '';

  if (!code) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        Authentication code is missing.
      </div>
    )
  } 

  return (
    <Suspense fallback={<div className="flex items-center justify-center min-h-screen">Loading...</div>}>
      <UserAuthPage providerTag={params.provider_tag} code={code} />
    </Suspense>
  )
}
