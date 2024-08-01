from microskel.service_template import ServiceTemplate
import gateway_module


class ServiceGateway(ServiceTemplate):
    def __init__(self, name):
        super().__init__(name)

    def get_python_modules(self):
        return super().get_python_modules() + [gateway_module]


if __name__ == "__main__":
    ServiceGateway("service_gateway").start()
