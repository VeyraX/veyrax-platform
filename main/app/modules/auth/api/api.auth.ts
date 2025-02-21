import { createClient } from '@/lib/utils/supabase/client'

const supabase = createClient()

export interface AuthError {
  message: string;
}

export const authApi = {
  login: async (email: string, password: string) => {
    try {
      const { data, error } = await supabase.auth.signInWithPassword({
        email,
        password,
      });

      if (error) throw error;
      return { data, error: null };
    } catch (error) {
      return { data: null, error: { message: 'An error occurred during login' } };
    }
  },

  register: async (email: string, password: string) => {
    try {
      const { data, error } = await supabase.auth.signUp({
        email,
        password
      });

      if (error) throw error;
      return { data, error: null };
    } catch (error) {
      return { data: null, error: { message: 'An error occurred during registration' } };
    }
  },

  loginWithGoogle: async () => {
    try {
      console.log('Starting Google OAuth login...');
      const { data, error } = await supabase.auth.signInWithOAuth({
        provider: 'google',
        options: {
          redirectTo: `${window.location.origin}/api/auth/callback`,
          queryParams: {
            access_type: 'offline',
            prompt: 'consent',
          },
        },
      });

      if (error) {
        console.error('Google OAuth error:', error);
        throw error;
      }
      
      console.log('Google OAuth success:', data);
      return { data, error: null };
    } catch (error) {
      console.error('Google OAuth exception:', error);
      return { data: null, error: { message: 'An error occurred during Google login' } };
    }
  },

  logout: async () => {
    try {
      const { error } = await supabase.auth.signOut();
      if (error) throw error;
      return { error: null };
    } catch (error) {
      return { error: { message: 'An error occurred during logout' } };
    }
  },

  forgotPassword: async (email: string) => {
    try {
      const { error } = await supabase.auth.resetPasswordForEmail(email, {
        redirectTo: `${window.location.origin}/reset-password`,
      });

      if (error) throw error;
      return { error: null };
    } catch (error) {
      return { error: { message: 'An error occurred while sending password reset email' } };
    }
  },

  loginWithTwitter: async () => {
    try {
      const { data, error } = await supabase.auth.signInWithOAuth({
        provider: 'twitter',
        options: {
          redirectTo: `${window.location.origin}/api/auth/callback`,
        },
      });

      if (error) throw error;
      return { data, error: null };
    } catch (error) {
      return { data: null, error: { message: 'An error occurred during Twitter login' } };
    }
  },
};