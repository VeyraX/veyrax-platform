import { useQuery } from '@tanstack/react-query'
import { getChat, getChats, getChatMessages } from './api.agent'

export const useGetChat = (chatId: string) => {
  return useQuery({
    queryKey: ['chat', chatId],
    queryFn: () => getChat(chatId),
    enabled: !!chatId
  })
}

export const useGetChats = () => {
  return useQuery({
    queryKey: ['chats'],
    queryFn: getChats
  })
}

export const useGetChatMessages = (chatId: string) => {
  return useQuery({
    queryKey: ['chat-messages', chatId],
    queryFn: () => getChatMessages(chatId),
    enabled: !!chatId
  })
}