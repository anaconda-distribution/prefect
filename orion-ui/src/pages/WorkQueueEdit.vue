<template>
  <p-layout-default>
    <template #header>
      <PageHeadingWorkQueueEdit :queue="workQueueDetails" />
    </template>

    <WorkQueueForm :work-queue="workQueueDetails" @submit="updateQueue" @cancel="goBack" />
  </p-layout-default>
</template>

<script lang="ts" setup>
  import { WorkQueueForm, PageHeadingWorkQueueEdit, IWorkQueueRequest } from '@prefecthq/orion-design'
  import { showToast } from '@prefecthq/prefect-design'
  import { useRouteParam } from '@prefecthq/vue-compositions'
  import router from '@/router'
  import { workQueuesApi } from '@/services/workQueuesApi'

  const workQueueId = useRouteParam('id')

  const workQueueDetails = await workQueuesApi.getWorkQueue(workQueueId.value)

  const goBack = (): void => {
    router.back()
  }

  const updateQueue = async (workQueue: IWorkQueueRequest): Promise<void> => {
    try {
      await workQueuesApi.updateWorkQueue(workQueueId.value, workQueue)
      showToast(`${workQueueDetails.name} updated`, 'success')
      goBack()
    } catch (error) {
      showToast('Error occurred while updating your queue', 'error')
      console.error(error)
    }
  }
</script>