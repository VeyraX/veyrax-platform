'use client'

import { FC, useState } from 'react'
import { Header } from '@/app/modules/general/components/header'
import { Button } from '@/components/ui/button'
import { ArrowLeft, ArrowUpRight } from 'lucide-react'
import Link from 'next/link'
import Image from 'next/image'
import FeedbackDialog from '@/app/modules/general/components/feedback-dialog'

interface GoogleIssuesPageProps {
  hideHeader?: boolean
}

const GoogleIssuesPage: FC<GoogleIssuesPageProps> = ({ hideHeader = false }) => {
  const [feedbackOpen, setFeedbackOpen] = useState(false);

  return (
    <div className="flex-1 flex flex-col relative h-[100vh] w-full">
      {!hideHeader && <Header isShowChat={false} />}

      <div className="flex-1 px-8 py-6 max-w-4xl mx-auto">
        <div className="mb-4">
          <Link href="/integrations">
            <Button variant="ghost" className="flex items-center gap-2">
              <ArrowLeft size={16} />
              Back to Integrations
            </Button>
          </Link>
        </div>

        <div className="mb-8">
          <h1 className="text-3xl font-bold tracking-tight">Google Integration Status</h1>
        </div>

        <div className="space-y-6">
          <div className="p-6 border rounded-lg bg-amber-50 border-amber-200">
            <h2 className="text-xl font-semibold mb-2">Google Verification in Progress</h2>
            <p className="mb-4">
              We recently launched our platform and are currently undergoing Google's verification process for our API scopes.
              This process typically takes up to 8 weeks to complete, but we didn't want to limit your access to these services
              while we wait.
            </p>
          </div>

          <div className="space-y-4">
            <h2 className="text-xl font-semibold">What You Might See</h2>
            <p>
              When connecting to Google services, you may encounter a security warning screen like the one below:
            </p>
            <div className="border rounded-lg p-4 bg-gray-50 flex justify-center">
              <Image 
                src="/images/google-warning-screen.png" 
                alt="Google Warning Screen" 
                width={500} 
                height={300}
                className="rounded-md shadow-sm"
              />
            </div>
          </div>

          <div className="space-y-4">
            <h2 className="text-xl font-semibold">How to Proceed</h2>
            <p>
              This is completely normal and safe to proceed. Here's how to continue:
            </p>
            <ol className="list-decimal pl-6 space-y-3">
              <li>
                When you see the warning screen, click on <strong>"Advanced"</strong> at the bottom left
              </li>
              <li>
                Then click on <strong>"Go to [Your App Name] (unsafe)"</strong> at the bottom of the page
              </li>
              <li>
                You'll be able to select which permissions you want to grant
              </li>
            </ol>
            <p>
              You can customize which scopes (permissions) you grant based on your specific needs. Our platform is flexible
              and will work with whatever level of access you're comfortable providing.
            </p>
          </div>

          <div className="p-6 border rounded-lg">
            <h2 className="text-xl font-semibold mb-2">Data Security</h2>
            <p>
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

export default GoogleIssuesPage
