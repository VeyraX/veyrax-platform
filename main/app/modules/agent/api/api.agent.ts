import { createClient } from '@/lib/utils/supabase/client'
import { Chat, CreateChatPayload, ChatMessage, CreateChatMessagePayload } from './types.agent'

const supabase = createClient()

export async function createChat(payload: CreateChatPayload): Promise<Chat> {
  const { data: { user } } = await supabase.auth.getUser()
  
  if (!user) {
    throw new Error('User not authenticated')
  }

  const { data, error } = await supabase
    .from('chats_chats')
    .insert({
      user_id: user.id,
      name: 'New Chat'
    })
    .select('*')
    .single()

  if (error) {
    throw error
  }

  return data
}

export async function createChatMessage(payload: CreateChatMessagePayload): Promise<ChatMessage> {
  const { data: { user } } = await supabase.auth.getUser()
  
  if (!user) {
    throw new Error('User not authenticated')
  }

  const { data, error } = await supabase
    .from('chats_messages')
    .insert({
      ...payload,
      metadata: payload.metadata ? JSON.stringify(payload.metadata) : null
    })
    .select('*')
    .single()

  console.log('Supabase response - Data:', data)
  console.log('Supabase response - Error:', error)

  if (error) {
    throw error
  }

  return data
}

export async function getChatMessages(chatId: string): Promise<ChatMessage[]> {
  const { data: { user } } = await supabase.auth.getUser()
  
  if (!user) {
    throw new Error('User not authenticated')
  }

  const { data, error } = await supabase
    .from('chats_messages')
    .select('*')
    .eq('chat_id', chatId)
    .order('created_at', { ascending: true })

  if (error) {
    throw error
  }
  console.log('Supabase response - Data:', data)
  console.log('Supabase response - Error:', error)

  return (data || []).map(msg => ({
    ...msg,
    metadata: typeof msg.metadata === 'string' ? JSON.parse(msg.metadata) : msg.metadata,
    parts: (msg.parts || []).map((p: any) => ({
      type: p.type,
      ...(p.type === 'text' ? { text: p.text } : {}),
      ...(p.type === 'tool-invocation' ? {
        toolInvocation: {
          toolCallId: p.toolInvocation.toolCallId,
          toolName: p.toolInvocation.toolName,
          args: p.toolInvocation.args,
          result: p.toolInvocation.result,
          state: p.toolInvocation.state
        }
      } : {})
    }))
  }))
}

export async function getChat(chatId: string): Promise<Chat> {
  const { data: { user } } = await supabase.auth.getUser()
  
  if (!user) {
    throw new Error('User not authenticated')
  }

  const { data, error } = await supabase
    .from('chats_chats')
    .select('*')
    .eq('id', chatId)
    .single()

  if (error) {
    throw error
  }

  return data
}

export async function getChats(): Promise<Chat[]> {
  const { data: { user } } = await supabase.auth.getUser()
  
  if (!user) {
    throw new Error('User not authenticated')
  }

  const { data, error } = await supabase
    .from('chats_chats')
    .select('*')
    .order('created_at', { ascending: false })

  if (error) {
    throw error
  }

  return data || [];
}

export async function updateMessageAccuracy(
  messageId: string, 
  chatId: string, 
  isAccurate: boolean
): Promise<void> {
  const { data: { user } } = await supabase.auth.getUser()
  
  if (!user) {
    throw new Error('User not authenticated')
  }

  const { error } = await supabase
    .from('chats_messages')
    .update({ is_accurate: isAccurate })
    .match({ 
      message_id: messageId,
      chat_id: chatId 
    })

  if (error) {
    throw error
  }
}

export async function updateChatTitle(chatId: string, firstMessage: string): Promise<{ title: string }> {
  const response = await fetch('/api/chat-title', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ 
      chatId,
      firstMessage 
    }),
  });

  if (!response.ok) {
    throw new Error('Failed to update chat title');
  }

  return response.json();
}