import { useQuery } from '@tanstack/react-query'
import { getUserProfile } from './api.settings'

export const useGetUserProfile = () => {
  return useQuery({
    queryKey: ['user-profile'],
    queryFn: getUserProfile
  })
}