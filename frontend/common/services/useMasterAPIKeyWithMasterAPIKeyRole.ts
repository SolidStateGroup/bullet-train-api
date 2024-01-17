import { Res } from 'common/types/responses'
import { Req } from 'common/types/requests'
import { service } from 'common/service'

export const masterAPIKeyWithMasterAPIKeyRoleService = service
  .enhanceEndpoints({ addTagTypes: ['MasterAPIKeyWithMasterAPIKeyRole'] })
  .injectEndpoints({
    endpoints: (builder) => ({
      deleteMasterAPIKeyWithMasterAPIKeyRoles: builder.mutation<
        Res['masterAPIKeyWithMasterAPIKeyRoles'],
        Req['deleteMasterAPIKeyWithMasterAPIKeyRoles']
      >({
        invalidatesTags: ['MasterAPIKeyWithMasterAPIKeyRole'],
        query: (query: Req['deleteMasterAPIKeyWithMasterAPIKeyRoles']) => ({
          method: 'DELETE',
          url: `organisations/${query.org_id}/master-api-keys/${query.prefix}/roles/${query.role_id}`,
        }),
      }),
      getMasterAPIKeyWithMasterAPIKeyRoles: builder.query<
        Res['masterAPIKeyWithMasterAPIKeyRoles'],
        Req['getMasterAPIKeyWithMasterAPIKeyRoles']
      >({
        providesTags: (res) => [
          { id: res?.id, type: 'MasterAPIKeyWithMasterAPIKeyRole' },
        ],
        query: (query: Req['getMasterAPIKeyWithMasterAPIKeyRoles']) => ({
          url: `organisations/${query.org_id}/master-api-keys/${query.prefix}/`,
        }),
      }),
      getRolesMasterAPIKeyWithMasterAPIKeyRoles: builder.query<
        Res['masterAPIKeyWithMasterAPIKeyRoles'],
        Req['getMasterAPIKeyWithMasterAPIKeyRoles']
      >({
        providesTags: (res) => [
          { id: res?.id, type: 'MasterAPIKeyWithMasterAPIKeyRole' },
        ],
        query: (query: Req['getMasterAPIKeyWithMasterAPIKeyRoles']) => ({
          url: `organisations/${query.org_id}/master-api-keys/${query.prefix}/roles/`,
        }),
      }),
      // END OF ENDPOINTS
    }),
  })

export async function getMasterAPIKeyWithMasterAPIKeyRoles(
  store: any,
  data: Req['getMasterAPIKeyWithMasterAPIKeyRoles'],
  options?: Parameters<
    typeof masterAPIKeyWithMasterAPIKeyRoleService.endpoints.getMasterAPIKeyWithMasterAPIKeyRoles.initiate
  >[1],
) {
  return store.dispatch(
    masterAPIKeyWithMasterAPIKeyRoleService.endpoints.getMasterAPIKeyWithMasterAPIKeyRoles.initiate(
      data,
      options,
    ),
  )
}

export async function getRolesMasterAPIKeyWithMasterAPIKeyRoles(
  store: any,
  data: Req['getMasterAPIKeyWithMasterAPIKeyRoles'],
  options?: Parameters<
    typeof masterAPIKeyWithMasterAPIKeyRoleService.endpoints.getRolesMasterAPIKeyWithMasterAPIKeyRoles.initiate
  >[1],
) {
  return store.dispatch(
    masterAPIKeyWithMasterAPIKeyRoleService.endpoints.getRolesMasterAPIKeyWithMasterAPIKeyRoles.initiate(
      data,
      options,
    ),
  )
}

export async function deleteMasterAPIKeyWithMasterAPIKeyRoles(
  store: any,
  data: Req['getMasterAPIKeyWithMasterAPIKeyRoles'],
  options?: Parameters<
    typeof masterAPIKeyWithMasterAPIKeyRoleService.endpoints.deleteMasterAPIKeyWithMasterAPIKeyRoles.initiate
  >[1],
) {
  return store.dispatch(
    masterAPIKeyWithMasterAPIKeyRoleService.endpoints.deleteMasterAPIKeyWithMasterAPIKeyRoles.initiate(
      data,
      options,
    ),
  )
}
// END OF FUNCTION_EXPORTS

export const {
  useDeletexMasterAPIKeyWithMasterAPIKeyRolesMutation,
  useGetMasterAPIKeyWithMasterAPIKeyRolesQuery,
  useGetRolesMasterAPIKeyWithMasterAPIKeyRolesQuery,
  // END OF EXPORTS
} = masterAPIKeyWithMasterAPIKeyRoleService

/* Usage examples:
const { data, isLoading } = useGetMasterAPIKeyWithMasterAPIKeyRolesQuery({ id: 2 }, {}) //get hook
const [createMasterAPIKeyWithMasterAPIKeyRoles, { isLoading, data, isSuccess }] = useCreateMasterAPIKeyWithMasterAPIKeyRolesMutation() //create hook
masterAPIKeyWithMasterAPIKeyRoleService.endpoints.getMasterAPIKeyWithMasterAPIKeyRoles.select({id: 2})(store.getState()) //access data from any function
*/
