import { useQuery } from '@tanstack/react-query'
import { getIntegrationsData, getUserConnectedTools, checkIndexStatus } from './api.integrations'


export const useGetProviders = () => {
  return useQuery({
    queryKey: ['providers'],
    queryFn: getIntegrationsData
  })
}

export const useGetUserConnectionTools = () => {
  return useQuery({
    queryKey: ['user-connected-tools'],
    queryFn: getUserConnectedTools,
  })
}

export const useCheckIndexStatus = (providerId: string) => {
  return useQuery({
    queryKey: ['index-status', providerId],
    queryFn: () => checkIndexStatus(providerId)
  })
}