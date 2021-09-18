from kubernetes import client, config
from kubernetes.client import configuration
import urllib.request as req
import psycopg2 #postgreSQL 모듈

db = psycopg2.connect(host='58.122.182.172',
                      dbname="postgres",
                      user="postgres",
                      password="cccr",
                      port=5432)
cur = db.cursor()


def main():
    contexts, active_context = config.list_kube_config_contexts()
                
    if not contexts:
        print("Cannot find any context in kube-config file.")
        return
    contexts = [context['name'] for context in contexts]
    cur.execute("CREATE TABLE cluster (cloud_id text, cluster_id text, pod_ip varchar, metadata_namespace text, metadata_name text);")

    for context1 in contexts:
        client1 = client.CoreV1Api(
        api_client=config.new_client_from_config(context=context1))

        def DBcommit():
            for i in client1.list_pod_for_all_namespaces().items:        
                cur.execute("INSERT INTO cluster (cloud_id, cluster_id, pod_ip, metadata_namespace, metadata_name) VALUES (%s, %s, %s, %s, %s)", (cloud, context1, i.status.pod_ip, i.metadata.namespace, i.metadata.name))
                db.commit()
                
        if(context1 == "wsl"):
            print("\nList of pods on %s:" % context1)
            cloud = "Local"
            DBcommit()
            print("DB commit")

        elif(context1 == "gke"):
            print("\nList of pods on %s:" % context1)
            cloud = "GKE"
            DBcommit()
            print("DB commit")

        elif(context1 == "eks"):
            print("\nList of pods on %s:" % context1)
            cloud = "Aws"
            DBcommit()
            print("DB commit")

        elif(context1 == "aks"):
            print("\nList of pods on %s:" % context1)
            cloud = "Azure"
            DBcommit()
            print("DB commit")

        else:
            print("cluser none")

if __name__ == '__main__':
    main()