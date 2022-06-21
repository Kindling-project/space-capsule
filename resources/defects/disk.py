import json

import click

# # 为 test-ns 下 label为 app=testdemo 的所有pod设置访问网络延时
# # space-capsule network-delay --time 3000 --offset 1000 --interface eth0 --local-port 8080,8081 --timeout 30
# # OPTION:
# ./space-capsule delay pod eth0 3000 testdelay -lport 8080 --labels app:bop
# --destination-ip string   目标 IP. 支持通过子网掩码来指定一个网段的IP地址, 例如 192.168.1.0/24. 则 192.168.1.0~192.168.1.255 都生效。你也可以指定固定的 IP，如 192.168.1.1 或者 192.168.1.1/32，也可以通过都号分隔多个参数，例如 192.168.1.1,192.168.2.1。
# --exclude-port string     排除掉的端口，默认会忽略掉通信的对端端口，目的是保留通信可用。可以指定多个，使用逗号分隔或者连接符表示范围，例如 22,8000 或者 8000-8010。 这个参数不能与 --local-port 或者 --remote-port 参数一起使用
# --exclude-ip string       排除受影响的 IP，支持通过子网掩码来指定一个网段的IP地址, 例如 192.168.1.0/24. 则 192.168.1.0~192.168.1.255 都生效。你也可以指定固定的 IP，如 192.168.1.1 或者 192.168.1.1/32，也可以通过都号分隔多个参数，例如 192.168.1.1,192.168.2.1。
# --interface string        网卡设备，例如 eth0 (必要参数)
# --local-port string       本地端口，一般是本机暴露服务的端口。可以指定多个，使用逗号分隔或者连接符表示范围，例如 80,8000-8080
# --offset string           延迟时间上下浮动的值, 单位是毫秒
# --remote-port string      远程端口，一般是要访问的外部暴露服务的端口。可以指定多个，使用逗号分隔或者连接符表示范围，例如 80,8000-8080
# --time string             延迟时间，单位是毫秒 (必要参数)
# --force                   强制覆盖已有的 tc 规则，请务必在明确之前的规则可覆盖的情况下使用
# --ignore-peer-port        针对添加 --exclude-port 参数，报 ss 命令找不到的情况下使用，忽略排除端口
# --timeout string          设定运行时长，单位是秒，通用参数


# # space-capsule undo  {experiment-name}
# space-capsule undo network-delay
import jsonpath

from resources.scenes.service_slow import select_pod_from_ready, field_selector
from spacecapsule.executor import bash_executor
from spacecapsule.history import store_experiment
from spacecapsule.k8s import executor_command_inside_namespaced_pod, prepare_api
from spacecapsule.template import chaosblade_resource, chaosblade_resource_script


@click.command()
@click.argument('scope')
@click.argument('experiment-name')
@click.option('--path', 'path')
@click.option('--size', 'size')
@click.option('--reserve', 'reserve')
@click.option('--percent', 'percent')
@click.option('--timeout', 'timeout')
@click.option('--labels', 'labels')
@click.option('--names', 'names')
def disk_fill(scope, experiment_name, path, size, reserve, percent, timeout, labels, names):
    args = locals()
    args['action'] = 'fill'
    args['target'] = 'disk'
    args['desc'] = 'disk fill'
    args['matchers'] = [
        {
            'name': 'path',
            'value': path
        },
        {
            'name': 'size',
            'value': size
        },
        {
            'name': 'reserve',
            'value': reserve
        },
        {
            'name': 'percent',
            'value': percent
        },
        {
            'name': 'timeout',
            'value': timeout
        },
        {
            'name': 'labels',
            'value': labels
        },
        {
            'name': 'names',
            'value': names
        }

    ]
    # defects_info(args)
    bash_executor(chaosblade_resource_script, chaosblade_resource, rollback_args, 'chaosbladeResource-rollback.sh',
                  args)


def disk_latency(pod, container, volume, methods, time, kube_config):
    api_instance = prepare_api(kube_config)
    pod_list = api_instance.list_namespaced_pod("practice")
    if pod is None:
        pod_ref = select_pod_from_ready(pod_list.items, None, None)
    else:
        pod_ref = select_pod_from_ready(pod_list.items, field_selector, {"key": "$.metadata.name", "value": pod})
    host_ip = pod_ref.status.host_ip
    containers_list = pod.ref.status.containerStatuses
    if container is not None:
        for container_ref in containers_list:
            if container_ref.name == container:
                container_id = container_ref.containerID
                break
    else:
        container_id = containers_list[0].containerID

    if container_id is None:
        print("Can not found container named " + container + " in target pod")
        exit(0)
    commands = "docker inspect " + container_id + " -f {{.State.Pid}}"
    daemon_list = api_instance.list_namespaced_pod('chaosblade')
    for daemon in daemon_list.items:
        if daemon.status.host_ip == host_ip:
            stdout, stderr = executor_command_inside_namespaced_pod(api_instance, 'chaosblade', daemon.metadata.name,
                                                                    commands)
            # TODO Execute command in daemonSet Pod
            io_latency_commands = "/opt/iolatency/iolatency start "
            executor_command_inside_namespaced_pod(api_instance, 'chaosblade', daemon.metadata.name,
                                                   io_latency_commands)

            check_status_command = "/opt/iolatency/iolatency status"
            stdout, stderr = executor_command_inside_namespaced_pod(api_instance, 'chaosblade', daemon.metadata.name,
                                                                    check_status_command)
            status = jsonpath.jsonpath(json.loads(stdout), "$.status")
            if status != "started":
                # TODO failed reason
                print("Inject Failed caused by ...!")

            # TODO Store experiment into history
            rollback_arg = {
                "pod": daemon.metadata.name,
                "namespace": 'chaosblade',
                "command": "/opt/iolatency/iolatency stop"
            }
            experiment_arg = {

            }
            store_experiment(experiment_arg, rollback_arg, status, None)
            print("IoLatency inject succeed!")
            exit(0)

    print("Can not found target pod to inject!")


def rollback_args(args):
    return {}
