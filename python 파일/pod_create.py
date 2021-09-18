### 주석 추가 예정

import time

from kubernetes import config
from kubernetes.client import Configuration
from kubernetes.client.api import core_v1_api
from kubernetes.client.rest import ApiException
from kubernetes.stream import stream


def exec_commands(api_instance):
    name = 'busybox-test'
    resp = None
    try: # 'busybox-test'와 일치하는 pod가 있는지 목록 읽어오기
        resp = api_instance.read_namespaced_pod(name=name,
                                                namespace='default')
    except ApiException as e:
        if e.status != 404: # 404 오류가 아니면
            print("Unknown error: %s" % e)
            exit(1)

    if not resp: #'busybox-test' pod가 없다면
        print("Pod %s does not exist. Creating it..." % name)
        pod_manifest = {
            'apiVersion': 'v1',
            'kind': 'Pod',
            'metadata': {
                'name': name
            },
            'spec': {
                'containers': [{
                    'image': 'busybox',
                    'name': 'sleep',
                    "args": [
                        "/bin/sh",
                        "-c",
                        "while true;do date;sleep 5; done"
                    ]
                }]
            }
        }
        # pod_manifest 정보로 pod 생성(create_namespaced_pod 메소드 사용)
        resp = api_instance.create_namespaced_pod(body=pod_manifest,
                                                  namespace='default')
        while True: 
        # pod 생성됐는지 읽어오기
            resp = api_instance.read_namespaced_pod(name=name,
                                                    namespace='default')
            if resp.status.phase != 'Pending':
                break
            time.sleep(1)
        print("Done.")

    # Calling exec and waiting for response
    exec_command = [
        '/bin/sh',
        '-c',
        'echo This message goes to stderr; echo This message goes to stdout']
    resp = stream(api_instance.connect_get_namespaced_pod_exec,
                  name,
                  'default',
                  command=exec_command,
                  stderr=True, stdin=False,
                  stdout=True, tty=False)
    print("Response: " + resp)

    # Calling exec interactively
    exec_command = ['/bin/sh']
    resp = stream(api_instance.connect_get_namespaced_pod_exec,
                  name,
                  'default',
                  command=exec_command,
                  stderr=True, stdin=True,
                  stdout=True, tty=False,
                  _preload_content=False)
    commands = [
        "echo This message goes to stdout",
        "echo \"This message goes to stderr\" >&2",
    ]

    while resp.is_open():
        resp.update(timeout=1)
        if resp.peek_stdout():
            print("STDOUT: %s" % resp.read_stdout())
        if resp.peek_stderr():
            print("STDERR: %s" % resp.read_stderr())
        if commands:
            c = commands.pop(0)
            print("Running command... %s\n" % c)
            resp.write_stdin(c + "\n")
        else:
            break

    resp.write_stdin("date\n")
    sdate = resp.readline_stdout(timeout=3)
    print("Server date command returns: %s" % sdate)
    resp.write_stdin("whoami\n")
    user = resp.readline_stdout(timeout=3)
    print("Server user is: %s" % user)
    resp.close()


def main():
    config.load_kube_config()
    try:
        c = Configuration().get_default_copy()
    except AttributeError:
        c = Configuration()
        c.assert_hostname = False
    Configuration.set_default(c)
    core_v1 = core_v1_api.CoreV1Api() #core_v1_api.CoreV1Api()를 해야 .read | create | delete namespace 가능

    exec_commands(core_v1)


if __name__ == '__main__':
    main()
