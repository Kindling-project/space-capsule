import click

from spacecapsule.executor import chaosblade_ssh_executor, chaosblade_ssh_jvm_executor
from spacecapsule.history import check_status


@click.command()
@click.option('--ip', 'ip', default='10.10.103.72')
@click.option('--user', 'user', default='root')
@click.option('--pwd', 'pwd', default='pwd')
@click.option('--interface', 'interface', default='ens192')
@click.option("--check_history", is_flag=True, default=True,
              is_eager=True, callback=check_status,
              help="Check experiment history", expose_value=False)
def case1_vm(ip, user, pwd, interface):
    command = '/opt/chaosblade/blade create network delay --time 3000 --offset 100 --interface ' + interface + ' --local-port 8080,8081'
    chaosblade_ssh_executor(ip, user, pwd, command, 'case1-vm')
    print("node network delay injected done！")


# 向服务节点注入丢包
@click.command()
@click.option('--ip', 'ip', default='10.10.103.72')
@click.option('--user', 'user', default='root')
@click.option('--pwd', 'pwd', default='pwd')
@click.option('--interface', 'interface', default='ens192')
@click.option("--check_history", is_flag=True, default=True,
              is_eager=True, callback=check_status,
              help="Check experiment history", expose_value=False)
def case3_vm(ip, user, pwd, interface):
    command = '/opt/chaosblade/blade create network loss --percent 70 --interface ' + interface + ' --local-port 8080,8081'
    chaosblade_ssh_executor(ip, user, pwd, command, 'case3-vm')


# # 向服务节点注入DNS异常
# def case6_dns():
#     print("TODO")


# 向服务节点添加资源过载，请求时间过长
@click.command()
@click.option('--ip', 'ip', default='10.10.103.73')
@click.option('--user', 'user', default='root')
@click.option('--pwd', 'pwd', default='pwd')
@click.option("--check_history", is_flag=True, default=True,
              is_eager=True, callback=check_status,
              help="Check experiment history", expose_value=False)
def case8_vm(ip, user, pwd):
    command = '/opt/chaosblade/blade create cpu load --cpu-count 4 --cpu-percent 90'
    chaosblade_ssh_executor(ip, user, pwd, command, 'case8-vm')


# 向Java代码注入死锁，无请求返回
@click.command()
@click.option('--ip', 'ip', default='10.10.103.72')
@click.option('--user', 'user', default='root')
@click.option('--pwd', 'pwd', default='Ab123456')
@click.option('--pid', 'pid', default='21262')
@click.option("--check_history", is_flag=True, default=True,
              is_eager=True, callback=check_status,
              help="Check experiment history", expose_value=False)
def case13_vm(ip, user, pwd, pid):
    chaosblade_ssh_jvm_executor(ip, user, pwd, None, pid, 'com.imooc.appoint.service.Impl.PracticeServiceImpl',
                                'httpTxn1', '/opt/chaosblade/scripts/DeadLockService.java', 'deadlock',
                                'case13-vm')


# 向Java代码注入未处理异常
@click.command()
@click.option('--ip', 'ip', default='10.10.103.73')
@click.option('--user', 'user', default='root')
@click.option('--pwd', 'pwd', default='Ab123456')
@click.option('--pid', 'pid', default='6634')
@click.option("--check_history", is_flag=True, default=True,
              is_eager=True, callback=check_status,
              help="Check experiment history", expose_value=False)
def case14_vm(ip, user, pwd, pid):
    chaosblade_ssh_jvm_executor(ip, user, pwd, None, pid, 'com.imooc.appoint.service.Impl.PracticeServiceImpl',
                                'httpTxn1', '/opt/chaosblade/scripts/BusinessCodeService.java', 'specifyReturnOb',
                                'case14-vm')
