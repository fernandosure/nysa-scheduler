import json
from nysa_aws.deploy import  deploy_new_ecs_service, destroy_ecs_service, describe_ecs_service
from nysa_aws.stack_definition import StackDefinition
from nysa_aws.ecs import EcsClient
from nysa_aws.utils import get_ecs_service_diff
from notifiers import NotifyScheduler, StdoutLogger, SlackNotifier


class MessageScheduler(object):

    def __init__(self, message):
        self.default_notifiers = [StdoutLogger()]
        self.message_handlers = [ClusterDeployHandler(message, self.default_notifiers)]
        self.message = message

    def execute(self):
        for processor in self.message_handlers:
            if processor.execute():
                self.message.delete()
                break


class ClusterDeployHandler(object):

    def __init__(self, msg, notifiers):
        json_msg = json.loads(msg.body)

        self._notifiers = notifiers
        self.event_type = json_msg.get(u'event_type')
        self.callback_url = json_msg.get(u'callback_url')
        self.cluster = json_msg.get(u'cluster')
        self.payload = json_msg.get(u'payload')

        if self.callback_url:
            self._notifiers.append(SlackNotifier(self.callback_url))

        self.notifier = NotifyScheduler(notifiers)

    def execute(self):
        if self.event_type == u'cluster-deploy':

            stack_definition = StackDefinition(self.payload)
            self.notifier.emit("INFO", "retrieving current services state...")

            client = EcsClient()
            ecs_cluster = client.get_single_cluster(self.cluster)
            services = ecs_cluster.get_all_services()

            for svc in stack_definition.services:
                service = next((x for x in services if x.name.lower() == svc.name.lower()), None)
                if service:
                    diff = get_ecs_service_diff(service, svc)
                    if len(diff) > 0:
                        if diff.get(u'image', None) or diff.get(u'environment', None):
                            new_td = svc.get_task_definition(self.cluster)
                            new_td = new_td.register_as_new_task_definition()
                            service.task_definition_arn = new_td.arn
                            self.notifier.emit("INFO",
                                               "deploying taskDefinition version:{} of {}".format(new_td.revision,
                                                                                                  service.name))

                        service.desired_count = svc.desired_count
                        service.update_service()
                    else:
                        self.notifier.emit("INFO",
                                           "skipping deployment for {} there are no new changes in the taskDefinition"
                                           .format(service.name))
                else:
                    deploy_new_ecs_service(self.cluster, stack_definition, svc)
            return True

        return False


class ServiceDestroyHandler(object):

    def __init__(self, msg, notifiers):
        json_msg = json.loads(msg)

        self._notifiers = notifiers
        self.event_type = json_msg.get(u'event_type')
        self.callback_url = json_msg.get(u'callback_url')
        self.cluster = json_msg.get(u'cluster')
        self.service = json_msg.get(u'service')

        if self.callback_url:
            self._notifiers.append(SlackNotifier(self.callback_url))

        self.notifier = NotifyScheduler(notifiers)

    def execute(self):
        if self.event_type == u'service-destroy':

            self.notifier.emit("INFO", "retrieving current services state...")
            client = EcsClient()
            ecs_cluster = client.get_single_cluster(self.cluster)
            service = ecs_cluster.get_single_service(self.service)

            self.notifier.emit("INFO", "destroying service {} in the {} cluster".format(service.name, self.cluster))
            destroy_ecs_service(self.cluster, service.arn)
            self.notifier.emit("INFO", "service destroyed")
            return True

        return False
