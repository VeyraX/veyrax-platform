'use client'

import { FC, useState } from 'react'
import { Header } from '@/app/modules/general/components/header'
import { Button } from '@/components/ui/button'
import { ArrowLeft, ArrowUpRight, ShieldAlert, Info, Lock } from 'lucide-react'
import Link from 'next/link'
import Image from 'next/image'
import FeedbackDialog from '@/app/modules/general/components/feedback-dialog'

interface GoogleIssuePageProps {
  hideHeader?: boolean
}

const GoogleIssuePage: FC<GoogleIssuePageProps> = ({ hideHeader = false }) => {
  const [feedbackOpen, setFeedbackOpen] = useState(false);
  
  return (
    <div className="flex-1 flex flex-col relative min-h-[100vh] w-full bg-white">
      {!hideHeader && <Header isShowChat={false} />}

      <div className="flex-1 max-w-4xl mx-auto px-6 py-8 md:py-12">
        {/* Page Header */}
        <div className="mb-8 flex items-center gap-2">
          <h1 className="text-2xl md:text-3xl font-bold tracking-tight">Google Integration Status</h1>
        </div>

        {/* Main Content - All sections in a single column */}
        <div className="space-y-6">
          {/* Alert Banner */}
          <div className="p-4 md:p-6 border rounded-lg bg-amber-50 border-amber-200 flex gap-3">
            <ShieldAlert className="h-5 w-5 text-amber-600 flex-shrink-0 mt-0.5" />
            <div>
              <h2 className="text-lg font-semibold mb-2 text-amber-800">Verification in Progress</h2>
              <p className="text-amber-700">
                We recently launched our platform and are currently undergoing Google's verification process for our API scopes.
                This process typically takes up to 8 weeks to complete, but we didn't want to limit your access to these services
                while we wait.
              </p>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg border shadow-sm">
            <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
              What You Might See
            </h2>
            <p className="mb-4 text-gray-700">
              When connecting to Google services, you may encounter a security warning screen like the one below:
            </p>
            <div className="p-4 flex justify-center bg-gray-50 rounded-lg border border-gray-100">
              <Image 
                src="/integrations/google-issue-0.png" 
                alt="Google Warning Screen" 
                width={500} 
                height={300}
                className="rounded-md shadow-sm border border-gray-200 object-contain"
              />
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg border shadow-sm">
            <h2 className="text-xl font-semibold mb-4">How to Proceed</h2>
            <p className="mb-4 text-gray-700">
              This is completely normal and safe to proceed. Here's how to continue:
            </p>
            
            <div className="space-y-6">
              <div className=" border-gray-200 pl-4 py-1">
                <p className="font-medium mb-2">Step 1: Click on <span className="bg-gray-100 px-1.5 py-0.5 rounded text-sm font-mono">Advanced</span> at the bottom left:</p>
                <div className="mt-3 bg-gray-50 p-4 rounded-lg border border-gray-100">
                  <Image 
                    src="/integrations/google-issue-1.png" 
                    alt="Click on Advanced" 
                    width={500} 
                    height={300}
                    className="rounded-md shadow-sm border border-gray-200 object-contain"
                  />
                </div>
              </div>
              
              <div className="border-gray-200 pl-4 py-1">
                <p className="font-medium mb-2">Step 2: Click on <span className="bg-gray-100 px-1.5 py-0.5 rounded text-sm font-mono">Go to VeyraX</span> at the bottom of the page:</p>
                <div className="mt-3 bg-gray-50 p-4 rounded-lg border border-gray-100">
                  <Image 
                    src="/integrations/google-issue-2.png" 
                    alt="Click on Go to App Name" 
                    width={500} 
                    height={300}
                    className="rounded-md shadow-sm border border-gray-200 object-contain"
                  />
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg border shadow-sm">
            <h2 className="text-lg font-semibold mb-3">Permissions</h2>
            <p className="text-gray-700 mb-4">
              You can customize which scopes (permissions) you grant based on your specific needs. Our platform is flexible
              and will work with whatever level of access you're comfortable providing.
            </p>
          </div>

          <div className="bg-white p-6 rounded-lg border shadow-sm">
            <h2 className="text-lg font-semibold mb-3 flex items-center gap-2">
              Data Security
            </h2>
            <p className="text-gray-700">
              We take your security seriously. All tokens we store are encrypted in accordance with our <Link href="/terms" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">Terms of Service</Link>.
              We only request the permissions necessary for the functionality you want to use.
            </p>
          </div>

          <div className="bg-white p-6 rounded-lg border shadow-sm">
            <h2 className="text-lg font-semibold mb-3">Need Help?</h2>
            <p className="text-gray-700 mb-4">
              If you have any questions or need assistance with the Google integration, our support team is here to help.
            </p>
            <div className="flex flex-col gap-2">
              <Button 
                variant="link" 
                size="sm" 
                className="justify-start"
                onClick={() => setFeedbackOpen(true)}
              >
                Ask a Question
                <ArrowUpRight className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>
      </div>
      
      <FeedbackDialog open={feedbackOpen} onOpenChange={setFeedbackOpen} />
    </div>
  )
}

export default GoogleIssuePage
