from .common import Cluster, ClusterJob, SLURMClusterJob
from . import TU_Dresden

def get_cluster(name: str) -> Cluster:
    if name in ["romeo", "Romeo"]:
        return TU_Dresden.Romeo()
    if name in ["barnard", "Barnard"]:
        return TU_Dresden.Barnard()
    if name in ["capella", "Capella"]:
        return TU_Dresden.Capella()
    if name in ["capellasharded", "CapellaSharded", "capella_sharded", "Capella_sharded"]:
        return TU_Dresden.CapellaSharded()
    else:
        raise ValueError(f"Cluster {name} is not known!")


def get_suitable_job(cluster: Cluster) -> ClusterJob:
    if cluster.type == "SLURM":
        return SLURMClusterJob()
    else:
        return ClusterJob()
