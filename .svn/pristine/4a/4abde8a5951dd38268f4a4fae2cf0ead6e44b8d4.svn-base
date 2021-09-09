import docker
import logging

log = logging.getLogger('service')


class DockerManager(object):

    def __init__(self) -> None:
        super().__init__()
        try:
            self.client = docker.DockerClient(base_url='unix://var/run/docker.sock')
        except Exception as e:
            log.error("Error on DockerClient:")
            log.exception(e)

    def start(self):
        pass

    def stop(self):
        pass

    def get_docker_version(self):
        return self.client.version()

    # 生成镜像 docker build
    def image_build(self, **kwargs):
        return self.client.images.build(**kwargs)

    # 获取单个镜像
    def image_one(self, name):
        try:
            image = self.client.images.get(name)
        except Exception as e:
            image = None
        return image

    # 删除单个镜像 docker rmi
    def image_remove(self, image, force=False, noprune=False):
        return self.client.images.remove(image, force, noprune)

    # 所有镜像列表 docker images
    def image_list(self, **kwargs):
        return self.client.images.list()

    # 创建并运行容器 docker run
    def container_run(self, image, command=None, **kwargs):
        pass

    # 创建容器 docker create
    def container_create(self, image, command=None, **kwargs):
        return self.client.containers.create(image, command, **kwargs)

    # 启动容器 docker start
    def container_start(self, name):
        # 根据名称或ID获取容器实例
        container = self.container_one(name)
        if container:
            container.start()
            return True
        else:
            return False

    # 停止容器 docker stop
    def container_stop(self, name):
        # 根据名称或ID获取容器实例
        container = self.container_one(name)
        if container:
            container.stop()
            return True
        else:
            return False

    # 重启容器 docker stop
    def container_restart(self, name):
        # 根据名称或ID获取容器实例
        container = self.container_one(name)
        if container:
            container.restart()
            return True
        else:
            return False

    # 查看所有容器 docker ps
    def container_list(self, **kwargs):
        return self.client.containers.list(**kwargs)

    # 获取单个容器
    def container_one(self, name):
        return self.client.containers.get(name)

    # 删除单个容器 docker rm
    # -f: 通过SIGKILL信号强制删除一个运行中的容器。
    # -l: 移除容器间的网络连接，而非容器本身。
    # -v: 删除与容器关联的卷。
    def container_remove(self, name, v=True, link=False, force=True):
        # 根据名称或ID获取容器实例
        container = self.container_one(name)
        if container:
            container.remove(v=v, link=link, force=force)
            return True
        else:
            return False




