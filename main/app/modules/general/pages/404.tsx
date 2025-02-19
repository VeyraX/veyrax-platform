'use client'

import { Button } from "@/components/ui/button"
import { useRouter } from "next/navigation";

export default function NotFound() {
  const router = useRouter();


  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-white p-4">
      <div className="max-w-md w-full text-center space-y-6">
        <h1 className="text-4xl font-bold text-gray-900">Oops!</h1>
        <p className="text-lg text-gray-600">
          The page you are looking for does not exist.
        </p>
        <p className="text-lg text-gray-600">
          Please check the URL and try again.
        </p>
        <div className="flex flex-col sm:flex-row justify-center gap-4">
          <Button variant="outline" className="w-full sm:w-auto" onClick={() => {
            router.push('/');
          }}>
            Return to homepage
          </Button>
          <Button className="w-full sm:w-auto" onClick={() => {
            router.back();
          }}>
            Return to previous page
          </Button>
        </div>
      </div>
    </div>
  )
}