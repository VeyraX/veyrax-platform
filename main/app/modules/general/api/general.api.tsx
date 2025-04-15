import { UserFeedback, FeedbackSubmitData, TeamRequestData, DeployWaitlistRequestData, ContactRequestData } from "./general.types"

import { createClient } from '@/lib/utils/supabase/client'

const supabase = createClient()

export const submitFeedback = async (feedbackData: FeedbackSubmitData): Promise<UserFeedback> => {
    const { data: { user } } = await supabase.auth.getUser()
    
    if (!user) {
      throw new Error('User not authenticated')
    }
    
    const { data, error } = await supabase
      .from('users_feedback')
      .insert({
        user_id: user.id,
        text: feedbackData.text,
        mood: feedbackData.mood
      })
      .select()
      .single()
    if (error) {
      console.error('Error submitting feedback:', error)
      throw error
    }
    
    return data as UserFeedback
  }

export const submitTeamRequest = async (requestData: TeamRequestData): Promise<void> => {
  const { error } = await supabase
    .from('users_team_requests')
    .insert({
      email: requestData.email,
      company: requestData.company
    })
  
  if (error) {
    console.error('Error submitting team request:', error)
    throw error
  }
}

export const submitDeployWaitlistRequest = async (requestData: DeployWaitlistRequestData): Promise<void> => {
  const { data: { user } } = await supabase.auth.getUser();
  
  if (!user) {
    throw new Error('User not authenticated');
  }
  
  const { error } = await supabase
    .from('deploy_waitlist')
    .insert({
      user_id: user.id,
      reason: requestData.reason,
      deploy_type: requestData.deploy_type,
    });
  
  if (error) {
    console.error('Error submitting deploy waitlist request:', error);
    throw error;
  }
};

export const submitContactRequest = async (requestData: ContactRequestData): Promise<void> => {
  const { error } = await supabase
    .from('contact_us_requests')
    .insert({
      email: requestData.email,
      reason: requestData.reason,
    });
  
  if (error) {
    console.error('Error submitting contact request:', error);
    throw error;
  }
};