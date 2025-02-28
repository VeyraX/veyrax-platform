import { useQuery } from '@tanstack/react-query'
import { getUserProfile, getUserApiKey } from './api.settings'

export const useGetUserProfile = () => {
  return useQuery({
    queryKey: ['user-profile'],
    queryFn: getUserProfile
  })
}

export const useGetUserApiKey = () => {
  return useQuery({
    queryKey: ['user-api-key'],
    queryFn: getUserApiKey
  })
}