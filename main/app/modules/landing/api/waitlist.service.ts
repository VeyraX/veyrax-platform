import { createClient } from '@/lib/utils/supabase/client'
import type { WaitlistUser } from '../types/waitlist.types'

export class WaitlistService {
  static async addToWaitlist(email: string): Promise<{ data: WaitlistUser | null; error: any }> {
    const supabase = createClient()
    
    const { error } = await supabase
      .from('users_waitlist')
      .insert([{ email }])
    
    return {
      data: error ? null : { email } as WaitlistUser,
      error
    }
  }
}