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

export interface TeamRequestData {
    email: string
    company: string
}

export interface Package {
    name: string
    description: string
    api_calls_limit: number
    flows_limit: number
    monthly_price: number
    yearly_price: number
}

export interface PackageInfo {
    name: string;
    description: string;
    api_calls_limit: number | string;
    flows_limit: number | string;
    monthly_price: number | null;
    yearly_price: number | null;
    custom_price?: string;
}

export interface DeployWaitlistRequestData {
    reason: string;
    deploy_type: string;
}

export interface ContactRequestData {
    email: string;
    reason: string;
}
