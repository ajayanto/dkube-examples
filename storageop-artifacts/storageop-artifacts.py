import os,kfp,json

search_path = os.path.dirname(os.path.abspath(__file__)) + "/../components"
component_store = kfp.components.ComponentStore(local_search_paths=[search_path])

dkube_storage_op = component_store.load_component("storage")

@kfp.dsl.pipeline(name='StorageOp',description='StorageOp component')

def storageop_artifacts(code,dataset,model):
    with kfp.dsl.ExitHandler(exit_op=storage_op("reclaim", namespace="kubeflow",uid="{{workflow.uid}}")):
            input_volumes = json.dumps(["{{workflow.uid}}-project@program://"+str(code),"{{workflow.uid}}-dataset@dataset://"+str(dataset),"{{workflow.uid}}-model@model://" + str(model)])
            storage  = storage_op("export", namespace="kubeflow", input_volumes=input_volumes)
            
            train = kfp.dsl.ContainerOp(
                name="step1",
                image="docker.io/ocdr/dkube-datascience-tf-cpu:v2.0.0-3",
                command="bash", 
                arguments=["-c", "ls /dataset"],
                pvolumes={
                         "/project": kfp.dsl.PipelineVolume(pvc="{{workflow.uid}}-project"),
                         "/dataset": kfp.dsl.PipelineVolume(pvc="{{workflow.uid}}-dataset"),
                         "/model": kfp.dsl.PipelineVolume(pvc="{{workflow.uid}}-model")
                         }).after(storage)
