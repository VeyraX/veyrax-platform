import { useQuery } from '@tanstack/react-query'
import { getIntegrationsData, getUserConnectedTools } from './api.integrations'


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