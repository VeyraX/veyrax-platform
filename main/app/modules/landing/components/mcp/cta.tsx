"use client";

import { Button } from "@/components/ui/button";
import { DotPattern } from "@/components/ui/dot-pattern";
import { Card, CardContent } from "@/components/ui/card";
import { useRouter } from 'next/navigation';
import { getUserProfile } from '@/app/modules/settings/api/api.settings';
import { useEffect, useState } from "react";
import { UserProfile } from '@/app/modules/settings/api/types.settings';
import Image from "next/image";
import { authApi } from '@/app/modules/auth/api/api.auth';
import { cn } from "@/lib/utils";

export function CTA() {
  const router = useRouter();
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [isGoogleLoading, setIsGoogleLoading] = useState(false);

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const data = await getUserProfile();
        setProfile(data);
      } catch (error) {
        console.error('Error fetching user profile:', error);
      }
    };
    
    fetchProfile();
  }, []);

  const handleEmailSignUp = () => {
    if (profile) {
      router.push('/integrations');
    } else {
      router.push('/register');
    }
  };

  const handleGoogleSignUp = async () => {
    if (profile) {
      router.push('/integrations');
      return;
    }

    setIsGoogleLoading(true);
    const { error } = await authApi.loginWithGoogle();
    if (error) {
      console.error('Google sign-up error:', error);
    } else {
      window.location.href = '/integrations';
    }
    setIsGoogleLoading(false);
  };

  return (
    <div className="w-full pt-8 pb-20">
      <div className="w-full h-full flex items-center justify-center px-4 md:px-8">
        <div className="container mx-auto">
          <Card className="relative overflow-hidden w-full max-w-7xl mx-auto">
            {/* Background pattern */}
            <div className="absolute inset-0">
              <DotPattern
                width={24}
                height={24}
                glow={true}
                className={cn(
                    "[mask-image:linear-gradient(to_bottom_right,white,transparent,transparent)] ",
                  )}
              />
              <DotPattern
                width={24}
                height={24}
                glow={true}
                className={cn(
                    "[mask-image:linear-gradient(to_top_left,white,transparent,transparent)] ",
                  )}
              />
            </div>

            {/* Content container */}
            <CardContent className="relative z-10 flex flex-col items-center gap-8 text-center py-16 px-8 sm:py-20 sm:px-12">
              {/* Heading */}
              <h2 className="text-5xl md:text-7xl max-w-3xl tracking-tighter text-center">
                <span className="font-regular">Make your Agents</span> <span className="font-semibold">really powerful with VeyraX MCP</span>
              </h2>

              {/* Description */}
              <p className="text-lg md:text-xl leading-relaxed tracking-tight text-muted-foreground max-w-2xl text-center">
                Integrate, deploy and manage all your tools in one place with a single API key. Try it today.
              </p>

              {/* CTA Buttons */}
              <div className="flex flex-row items-center gap-4 w-full max-w-md justify-center">
                {profile ? (
                  <Button 
                    className="gap-2"
                    onClick={() => router.push('/integrations')}
                  >
                    Explore Integrations
                  </Button>
                ) : (
                  <>
                    <Button 
                      className="gap-2"
                      onClick={handleEmailSignUp}
                    >
                      Sign up with email
                    </Button>
                    
                    <Button 
                      variant="outline" 
                      className="flex items-center gap-2"
                      onClick={handleGoogleSignUp}
                      disabled={isGoogleLoading}
                    >
                      <Image 
                        src="/logos/google-logo.svg" 
                        alt="Google logo" 
                        width={16} 
                        height={16} 
                      />
                      <span>Sign up with Google</span>
                    </Button>
                  </>
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
} 