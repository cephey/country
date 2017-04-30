from cacheback.base import Job
from apps.pages.models import Partition, Resource
from apps.utils.jobs import Job


class IndexOppositionPartitionResourcesJob(Job):

    def fetch(self):
        partitions = []
        for partition in Partition.objects.active().order_by('id'):
            partitions.append({
                'partition': partition,
                'resources': Resource.objects.active().filter(partition=partition).order_by('-rating')[:5]
            })
        return partitions
