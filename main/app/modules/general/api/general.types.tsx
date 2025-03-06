export interface UserFeedback {
    id: string
    user_id: string
    text: string
    mood: string
    created_at: string
}


export interface FeedbackSubmitData {
    text: string
    mood: string
}