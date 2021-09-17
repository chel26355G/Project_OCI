from kubernetes import client, config
from kubernetes.client import configuration


def main():
    contexts, active_context = config.list_kube_config_contexts()
    if not contexts:
        print("Cannot find any context in kube-config file.")
        return
    contexts = [context['name'] for context in contexts]
    for context1 in contexts:
        print(context1)
        client1 = client.CoreV1Api(
            api_client=config.new_client_from_config(context=context1))

        print("\nList of pods on %s:" % context1)
        # for i in client1.list_pod_for_all_namespaces().items:
        #     print("%s\t%s\t%s\t%s" %
        #           (i.status.pod_ip, i.metadata.namespace, i.metadata.name, i.status.))

        for i in client1.list_node():
            print(i)


if __name__ == '__main__':
    main()
